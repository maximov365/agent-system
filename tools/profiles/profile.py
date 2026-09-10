#!/usr/bin/env python3
"""Project-owned quality checks. Validation never executes commands."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

KINDS = {'web', 'mobile', 'desktop', 'game', 'service', 'content'}
ID = re.compile(r'^[a-z0-9][a-z0-9_-]{0,79}$')


def inside(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or '..' in Path(relative).parts or '.git' in Path(relative).parts:
        raise ValueError('Expected a contained project-relative path')
    current = root
    for part in Path(relative).parts:
        current /= part
        if current.is_symlink():
            raise ValueError('Symlinked profile/check/evidence path')
    return current


def validate(data, root):
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Unsupported quality profile schema')
    if not isinstance(data.get('kinds'), list) or not data['kinds'] or any(k not in KINDS for k in data['kinds']):
        raise ValueError('Profile needs supported kinds')
    if not isinstance(data.get('targets'), list) or not data['targets'] or not all(isinstance(t, str) and t for t in data['targets']):
        raise ValueError('Profile needs explicit device/runtime targets')
    checks = data.get('checks')
    if not isinstance(checks, list) or not checks:
        raise ValueError('Profile needs checks (unavailable with reason is allowed)')
    seen = set()
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get('id'), str) or not ID.fullmatch(check['id']) or check['id'] in seen:
            raise ValueError('Invalid/duplicate check ID')
        seen.add(check['id'])
        state = check.get('status')
        if state == 'unavailable':
            if not isinstance(check.get('reason'), str) or not check['reason'].strip() or 'command' in check:
                raise ValueError('Unavailable check requires a reason and no command')
            continue
        if state != 'configured':
            raise ValueError('Check status must be configured or unavailable; results belong in evidence')
        command = check.get('command')
        if not isinstance(command, list) or not command or not all(isinstance(v, str) and v and '\0' not in v for v in command):
            raise ValueError('Check command must be an argv array')
        if not inside(root, check.get('cwd', '.')).is_dir():
            raise ValueError('Check working directory is missing')
        timeout = check.get('timeout_seconds', 300)
        if type(timeout) is not int or not 1 <= timeout <= 1800:
            raise ValueError('Check timeout must be 1..1800 seconds')
        evidence = check.get('defined_by')
        if not isinstance(evidence, list) or not evidence or not all(inside(root, p).is_file() for p in evidence):
            raise ValueError('Configured check requires existing source evidence')
    budgets = data.get('budgets', [])
    if not isinstance(budgets, list):
        raise ValueError('Budgets must be a list')
    for budget in budgets:
        if not isinstance(budget, dict) or not all(isinstance(budget.get(k), str) and budget[k] for k in ['metric', 'unit', 'target', 'measurement']):
            raise ValueError('Budget needs metric, unit, target device, and measurement method')
        limit = budget.get('limit')
        if type(limit) not in (int, float) or not math.isfinite(limit) or limit <= 0:
            raise ValueError('Budget limit must be positive and finite')
    return data


def run_check(data, root, check_id, output):
    validate(data, root)
    check = next((c for c in data['checks'] if c['id'] == check_id), None)
    if check is None:
        raise ValueError('Unknown check ID')
    if check['status'] != 'configured':
        raise ValueError('Check unavailable: ' + check['reason'])
    # Output is validated independently of CLI callers. Never overwrite evidence.
    output = inside(root, str(output.relative_to(root)))
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    result = {'schema_version': 1, 'check': check_id, 'command': check['command'],
              'profile_sha256': hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest(),
              'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'failed',
              'exit_code': None, 'elapsed_seconds': None, 'visual_review': 'not_performed'}
    process = None
    try:
        with (output / 'output.log').open('wb') as log:
            process = subprocess.Popen(check['command'], cwd=inside(root, check.get('cwd', '.')),
                                       stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=os.name == 'posix')
            result['exit_code'] = process.wait(timeout=check.get('timeout_seconds', 300))
            result['status'] = 'passed' if result['exit_code'] == 0 else 'failed'
    except subprocess.TimeoutExpired:
        result['status'] = 'timed_out'
    except OSError as error:
        result['error'] = str(error)
    finally:
        if process:
            if os.name == 'posix':
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            elif process.poll() is None:
                process.kill()
            process.wait()
        result['elapsed_seconds'] = round(time.monotonic() - start, 3)
        (output / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['validate', 'run'])
    parser.add_argument('--project', default='.')
    parser.add_argument('--profile', default='quality/profile.json')
    parser.add_argument('--check')
    parser.add_argument('--output')
    args = parser.parse_args()
    try:
        root = Path(args.project).resolve()
        data = validate(json.loads(inside(root, args.profile).read_text()), root)
        if args.action == 'validate':
            print(json.dumps({'valid': True, 'kinds': data['kinds'], 'checks': len(data['checks']), 'executed': False}))
            return 0
        if not args.check:
            raise ValueError('Run requires one explicit --check ID')
        output = inside(root, args.output or '.agent/evidence/quality/' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
        result = run_check(data, root, args.check, output)
        print(json.dumps({**result, 'evidence': str(output)}))
        return 0 if result['status'] == 'passed' else 1
    except (ValueError, OSError, TypeError) as error:
        print('Quality profile: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
