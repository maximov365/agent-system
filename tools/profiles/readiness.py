"""Read-only project prerequisites and explicit, loopback-only HTTP probes."""
import http.client
import os
from pathlib import Path
import shutil
from urllib.parse import urlsplit


def local_url(value):
    if not isinstance(value, str) or any(ord(c) < 33 for c in value):
        raise ValueError('Launch URL must be a local HTTP URL')
    url = urlsplit(value)
    if (url.scheme != 'http' or url.hostname not in {'127.0.0.1', '::1', 'localhost'}
            or url.username is not None or url.password is not None or url.fragment):
        raise ValueError('Launch URL requires HTTP on literal loopback or localhost; no credentials/fragment')
    if url.port is not None and not 1 <= url.port <= 65535:
        raise ValueError('Invalid launch port')
    return url


def validate_readiness(data, root, inside):
    config = data.get('readiness', {})
    if not isinstance(config, dict) or set(config) - {'requirements', 'model', 'launch'}:
        raise ValueError('Readiness supports requirements, model and launch')
    requirements = config.get('requirements', [])
    if not isinstance(requirements, list) or len(requirements) > 30:
        raise ValueError('Readiness needs at most 30 requirements')
    names = set()
    for item in requirements:
        if (not isinstance(item, dict) or not isinstance(item.get('id'), str)
                or not item['id'].strip() or item['id'] in names):
            raise ValueError('Readiness requirement needs a unique ID')
        names.add(item['id'])
        if set(item) - {'id', 'executable', 'paths', 'help'}:
            raise ValueError('Unknown readiness requirement field')
        executable = item.get('executable')
        paths = item.get('paths', [])
        if executable is not None and (not isinstance(executable, str) or not executable or '\0' in executable):
            raise ValueError('Readiness executable must be a name/path, not a command array')
        if not isinstance(paths, list) or len(paths) > 30:
            raise ValueError('Readiness paths must be a bounded list')
        for path in paths:
            inside(root, path)  # Missing prerequisites are findings, not schema errors.
        if executable is None and not paths:
            raise ValueError('Readiness requirement needs an executable or paths')
        if not isinstance(item.get('help'), str) or not item['help'].strip():
            raise ValueError('Readiness requirement needs an actionable help message')
    model = config.get('model', {})
    if (not isinstance(model, dict) or set(model) - {'requested', 'reasoning_effort', 'service_tier'}
            or any(not isinstance(v, str) or not v.strip() for v in model.values())):
        raise ValueError('Model intent supports requested, reasoning_effort and service_tier strings')
    launch = config.get('launch')
    if launch is not None:
        if not isinstance(launch, dict) or set(launch) - {'command', 'cwd', 'defined_by', 'url', 'expected_text', 'verification_check'}:
            raise ValueError('Invalid launch contract')
        command = launch.get('command')
        if not isinstance(command, list) or not command or not all(isinstance(s, str) and s and '\0' not in s for s in command):
            raise ValueError('Launch command must be an argv array')
        if not inside(root, launch.get('cwd', '.')).is_dir():
            raise ValueError('Launch working directory is missing')
        sources = launch.get('defined_by')
        if not isinstance(sources, list) or not sources or not all(inside(root, p).is_file() for p in sources):
            raise ValueError('Launch requires existing source evidence')
        local_url(launch.get('url'))
        expected = launch.get('expected_text')
        if expected is not None and (not isinstance(expected, str) or not 1 <= len(expected) <= 200):
            raise ValueError('Expected HTTP text must be 1..200 characters')
        check_id = launch.get('verification_check')
        if check_id is not None and not any(c['id'] == check_id and c['status'] == 'configured' for c in data['checks']):
            raise ValueError('Launch verification must reference a configured project check')


def executable_path(command, cwd):
    if os.path.dirname(command):
        path = Path(command) if Path(command).is_absolute() else cwd / command
        return str(path) if path.is_file() and os.access(path, os.X_OK) else None
    search = os.pathsep.join(str((cwd / p).resolve()) for p in os.get_exec_path())
    return shutil.which(command, path=search)


def probe_http(launch):
    """Never follow redirects, use proxies, send credentials or read full pages."""
    url = local_url(launch['url'])
    host = '127.0.0.1' if url.hostname == 'localhost' else url.hostname
    connection = http.client.HTTPConnection(host, url.port or 80, timeout=3)
    result = {'status': 'unreachable', 'url': launch['url'], 'status_code': None,
              'interaction_verified': False}
    try:
        connection.request('GET', (url.path or '/') + ('?' + url.query if url.query else ''))
        response = connection.getresponse()
        result['status_code'] = response.status
        body = response.read(65536).decode('utf-8', errors='replace')
        expected = launch.get('expected_text')
        result['status'] = ('responding' if response.status == 200 and (expected is None or expected in body)
                            else 'unexpected_response')
        result['identity_checked'] = expected is not None
    except (OSError, http.client.HTTPException) as error:
        result['error'] = type(error).__name__
    finally:
        connection.close()
    return result


def diagnose(data, root, inside, *, probe=False):
    config = data.get('readiness', {})
    findings = []
    for item in config.get('requirements', []):
        missing = [p for p in item.get('paths', []) if not inside(root, p).exists()]
        resolved = executable_path(item['executable'], root) if 'executable' in item else None
        ok = not missing and ('executable' not in item or resolved is not None)
        findings.append({'id': item['id'], 'status': 'present' if ok else 'missing',
                         'missing_paths': missing, 'executable': resolved, 'help': item['help']})
    commands = []
    for check in data['checks']:
        if check['status'] == 'unavailable':
            commands.append({'id': check['id'], 'status': 'unavailable', 'reason': check['reason']})
        else:
            resolved = executable_path(check['command'][0], inside(root, check.get('cwd', '.')))
            commands.append({'id': check['id'], 'status': 'executable_found' if resolved else 'executable_missing',
                             'executable': resolved, 'result': 'not_run'})
    launch = config.get('launch')
    launch_report = {'status': 'not_configured'}
    if launch is not None:
        resolved = executable_path(launch['command'][0], inside(root, launch.get('cwd', '.')))
        launch_report = {**launch, 'status': 'configured' if resolved else 'executable_missing',
                         'executable': resolved, 'started': False}
    if probe and launch is None:
        raise ValueError('HTTP probe requires a configured launch contract')
    attention = (any(f['status'] == 'missing' for f in findings)
                 or any(c['status'] == 'executable_missing' for c in commands)
                 or launch_report['status'] == 'executable_missing')
    http = probe_http(launch) if probe else {'status': 'not_checked', 'interaction_verified': False}
    attention |= probe and http['status'] != 'responding'
    return {'schema_version': 1, 'status': 'attention' if attention else 'inspected',
            'requirements': findings, 'requirements_declared': bool(config.get('requirements')),
            'checks': commands, 'launch': launch_report, 'http': http,
            'model': {'intent': config.get('model', {}), 'observed': None,
                      'note': 'Project intent does not configure or prove the active host model, effort or tier.'},
            'commands_executed': False, 'journey': {'status': 'not_verified'},
            'visual_review': 'not_performed',
            'limitations': ['Executable presence does not verify versions or installed libraries.',
                            'Host tools, account eligibility and device access require session evidence.',
                            'HTTP response does not verify JavaScript, interactions or visual quality.']}
