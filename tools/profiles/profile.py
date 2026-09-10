#!/usr/bin/env python3
"""Project-owned quality checks. Validation never executes commands."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import stat
import subprocess
import sys
import time

KINDS = {'web', 'mobile', 'desktop', 'game', 'service', 'content', 'tooling'}
ID = re.compile(r'^[a-z0-9][a-z0-9_-]{0,79}$')
MAX_INPUT_FILES = 20000
MAX_INPUT_BYTES = 512 * 1024 * 1024


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
    navigation = data.get('navigation', {})
    if not isinstance(navigation, dict) or set(navigation) - {'source', 'tests', 'references'}:
        raise ValueError('Navigation supports source, tests and references')
    for paths in navigation.values():
        if not isinstance(paths, list) or len(paths) > 30 or not all(inside(root, p).exists() for p in paths):
            raise ValueError('Navigation needs at most 30 existing paths per category')
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
        policy = check.get('reuse')
        if policy is not None:
            if not isinstance(policy, dict) or policy.get('deterministic') is not True or policy.get('side_effect_free') is not True:
                raise ValueError('Reuse requires deterministic, side-effect-free checks')
            if not isinstance(policy.get('dependency_review'), str) or not policy['dependency_review'].strip():
                raise ValueError('Reuse needs a documented dependency review')
            for key in ['inputs', 'runtime_inputs']:
                paths = policy.get(key)
                if not isinstance(paths, list) or len(paths) > 100 or not all(isinstance(p, str) and p for p in paths):
                    raise ValueError('Reuse requires explicit inputs and runtime_inputs lists')
                for p in paths:
                    if key == 'inputs' or not Path(p).is_absolute():
                        inside(root, p)
            if not policy['inputs']:
                raise ValueError('Reuse requires nonempty inputs')
            age = policy.get('max_age_seconds')
            if type(age) is not int or not 1 <= age <= 900:
                raise ValueError('Reuse age must be 1..900 seconds')
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


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprint(data, root, check, session):
    """Hash declared closure, never infer it from git status or timestamps."""
    policy = check.get('reuse')
    if policy is None or session is None:
        return None, 'No reviewed reuse policy and explicit session'
    try:
        cwd = inside(root, check.get('cwd', '.'))
        command = check['command'][0]
        # Match subprocess resolution, including relative PATH entries.
        if os.path.dirname(command):
            executable = (cwd / command).resolve(strict=True)
        else:
            search = os.pathsep.join(str((cwd / p).resolve()) for p in os.get_exec_path())
            found = shutil.which(command, path=search)
            if not found:
                raise ValueError('Executable unavailable')
            executable = Path(found).resolve(strict=True)
        paths = [inside(root, p) for p in policy['inputs'] + check['defined_by']]
        paths += [Path(p) if Path(p).is_absolute() else inside(root, p) for p in policy['runtime_inputs']]
        paths += [executable, Path(__file__).resolve()]
        files = {}; total = 0
        def visit(path):
            nonlocal total
            # Reject symlinks anywhere in declared trees, including external runtime parents.
            if any(p.is_symlink() for p in [path, *path.parents]):
                raise ValueError('Symlink in declared inputs; run fresh or declare resolved runtime paths')
            name = str(path)
            if name in files:
                return
            mode = path.stat().st_mode
            if stat.S_ISDIR(mode):
                files[name] = ['directory', stat.S_IMODE(mode)]
                for child in sorted(path.iterdir()):
                    visit(child)
            elif stat.S_ISREG(mode):
                total += path.stat().st_size
                if total > MAX_INPUT_BYTES:
                    raise ValueError('Declared inputs exceed hashing byte budget')
                files[name] = [sha256(path), stat.S_IMODE(mode)]
            else:
                raise ValueError('Non-regular declared input')
            if len(files) > MAX_INPUT_FILES:
                raise ValueError('Declared inputs exceed hashing file budget')
        for path in paths:
            visit(path)
        payload = {'profile': data, 'files': files, 'root': str(root), 'cwd': str(cwd),
                   'executable': str(executable), 'platform': list(platform.uname()),
                   'environment': dict(os.environ), 'session': session}
        # Persist one digest only, never environment values or individual secret hashes.
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(), None
    except (OSError, ValueError, RecursionError) as error:
        return None, str(error)


def reusable_evidence(root, previous, key, check, session):
    if key is None:
        return None, 'Current inputs are not eligible'
    try:
        previous = inside(root, str(previous.relative_to(root)))
        report_path = inside(root, str((previous / 'report.json').relative_to(root)))
        log = inside(root, str((previous / 'output.log').relative_to(root)))
        seal = inside(root, str((previous / 'report.sha256').relative_to(root)))
        if not report_path.is_file() or report_path.stat().st_size > 65536 or not log.is_file():
            raise ValueError('Missing or oversized evidence')
        raw = report_path.read_bytes()
        if seal.read_text().strip() != hashlib.sha256(raw).hexdigest():
            raise ValueError('Evidence integrity mismatch')
        report = json.loads(raw)
        age = time.time() - datetime.fromisoformat(report['finished_at']).timestamp()
        if (report.get('status') != 'passed' or report.get('executed') is not True
                or report.get('exit_code') != 0 or report.get('reusable') is not True
                or report.get('check') != check['id'] or report.get('session') != session
                or report.get('fingerprint') != key
                or not 0 <= age <= check['reuse']['max_age_seconds']
                or report.get('log_sha256') != sha256(log)):
            raise ValueError('Evidence failed status, inputs, session, age or log validation')
        return report, None
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        return None, str(error)


def save_report(output, result):
    raw = (json.dumps(result, indent=2) + '\n').encode()
    (output / 'report.json').write_bytes(raw)
    (output / 'report.sha256').write_text(hashlib.sha256(raw).hexdigest() + '\n')


def run_check(data, root, check_id, output, *, session=None, reuse_from=None, fresh=False):
    validate(data, root)
    check = next((c for c in data['checks'] if c['id'] == check_id), None)
    if check is None:
        raise ValueError('Unknown check ID')
    if check['status'] != 'configured':
        raise ValueError('Check unavailable: ' + check['reason'])
    if session is not None and (not isinstance(session, str) or not ID.fullmatch(session)):
        raise ValueError('Session must be a short task ID')
    if reuse_from is not None and (session is None or fresh):
        raise ValueError('Reuse requires a session and cannot be combined with fresh')
    # Output is validated independently of CLI callers. Never overwrite evidence.
    output = inside(root, str(output.relative_to(root)))
    start = time.monotonic()
    before, ineligible = (None, 'Fresh execution requested') if fresh else fingerprint(data, root, check, session)
    previous, miss = reusable_evidence(root, reuse_from, before, check, session) if reuse_from is not None else (None, None)
    output.mkdir(parents=True, exist_ok=False)
    result = {'schema_version': 1, 'check': check_id, 'command': check['command'],
              'profile_sha256': hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest(),
              'started_at': datetime.now(timezone.utc).isoformat(), 'status': 'failed',
              'exit_code': None, 'elapsed_seconds': None, 'visual_review': 'not_performed',
              'executed': True, 'session': session, 'fingerprint': before, 'reusable': False,
              'reuse_note': miss or ineligible}
    if previous is not None:
        result.update(status='reused', executed=False, original_evidence=str(reuse_from.relative_to(root)),
                      original_finished_at=previous['finished_at'],
                      elapsed_seconds=round(time.monotonic() - start, 3),
                      finished_at=datetime.now(timezone.utc).isoformat())
        save_report(output, result)
        return result
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
        if before is not None and result['status'] == 'passed':
            after, note = fingerprint(data, root, check, session)
            result['reusable'] = before == after
            if not result['reusable']:
                result['reuse_note'] = note or 'Inputs changed during execution'
        result['finished_at'] = datetime.now(timezone.utc).isoformat()
        result['log_sha256'] = sha256(output / 'output.log')
        result['elapsed_seconds'] = round(time.monotonic() - start, 3)
        save_report(output, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['validate', 'summary', 'run'])
    parser.add_argument('--project', default='.')
    parser.add_argument('--profile', default='quality/profile.json')
    parser.add_argument('--check')
    parser.add_argument('--output')
    parser.add_argument('--session', help='Task-scoped ID; needed to record reusable evidence')
    reuse = parser.add_mutually_exclusive_group()
    reuse.add_argument('--reuse-from', help='Explicit original evidence directory; mismatch runs fresh')
    reuse.add_argument('--fresh', action='store_true', help='Always execute; required for release/security approval')
    args = parser.parse_args()
    try:
        root = Path(args.project).resolve()
        data = validate(json.loads(inside(root, args.profile).read_text()), root)
        if args.action == 'validate':
            print(json.dumps({'valid': True, 'kinds': data['kinds'], 'checks': len(data['checks']), 'executed': False}))
            return 0
        if args.action == 'summary':
            print(json.dumps({'kinds': data['kinds'], 'targets': data['targets'],
                              'navigation': data.get('navigation', {}),
                              'checks': [{k: c[k] for k in ['id', 'status', 'command', 'cwd', 'reason'] if k in c}
                                         for c in data['checks']], 'executed': False}, indent=2))
            return 0
        if not args.check:
            raise ValueError('Run requires one explicit --check ID')
        output = inside(root, args.output or '.agent/evidence/quality/' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
        result = run_check(data, root, args.check, output, session=args.session,
                           reuse_from=inside(root, args.reuse_from) if args.reuse_from else None, fresh=args.fresh)
        print(json.dumps({k: result.get(k) for k in ['check', 'status', 'executed', 'elapsed_seconds', 'reuse_note']} | {'evidence': str(output)}))
        return 0 if result['status'] in {'passed', 'reused'} else 1
    except (ValueError, OSError, TypeError) as error:
        print('Quality profile: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
