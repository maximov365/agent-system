"""Offline guard for this repository's CI workflows and reference templates.

Policy reviewed 2026-10-31. This checks declared settings, not action contents,
application builds, advisory databases or arbitrary GitHub expression semantics.
"""
from pathlib import Path
import re
import yaml


def values(value, workflow, job):
    """Resolve only the simple expressions used in these maintained templates."""
    if not isinstance(value, str) or '${{' not in value:
        return [value]
    match = re.fullmatch(r"\$\{\{\s*(env|matrix)\.(\w+)\s*\}\}", value)
    if match:
        scope, key = match.groups()
        source = ({**workflow.get('env', {}), **job.get('env', {})} if scope == 'env'
                  else job.get('strategy', {}).get('matrix', {}))
        found = source.get(key, [])
        found = found if isinstance(found, list) else [found]
        return [item for part in found for item in values(part, workflow, job)]
    match = re.fullmatch(r"\$\{\{\s*inputs\.(\w+)\s*\|\|\s*'([^']+)'\s*\}\}", value)
    if match:
        key, fallback = match.groups()
        # PyYAML's YAML 1.1 loader reads unquoted `on` as True.
        trigger = workflow.get('on', workflow.get(True, {}))
        options = trigger.get('workflow_dispatch', {}).get('inputs', {}).get(key, {}).get('options', [])
        return [fallback, *options]
    return []


def check_document(workflow):
    errors = []
    if not isinstance(workflow, dict) or not isinstance(workflow.get('jobs'), dict) or not workflow['jobs']:
        return ['Expected a workflow mapping with nonempty jobs']
    if workflow.get('permissions') != {'contents': 'read'}:
        errors.append('Workflow permissions must default to contents: read')
    for name, job in workflow['jobs'].items():
        if not isinstance(job, dict):
            errors.append(f'{name}: expected a job mapping')
            continue
        timeout = job.get('timeout-minutes')
        if type(timeout) is not int or not 1 <= timeout <= 60:
            errors.append(f'{name}: set a bounded timeout-minutes (1..60)')
        runners = values(job.get('runs-on'), workflow, job)
        if not runners or any(not isinstance(v, str) or not re.fullmatch(r'(ubuntu-\d{2}\.\d{2}|macos-\d+)', v) for v in runners):
            errors.append(f'{name}: use explicit supported-family runner labels')
        permissions = job.get('permissions', {'contents': 'read'})
        if permissions not in ({'contents': 'read'}, {'contents': 'write'}):
            errors.append(f'{name}: unexpected job permissions')
        elif permissions == {'contents': 'write'} and not job.get('if'):
            errors.append(f'{name}: write permissions need an explicit publishing condition')
        steps = job.get('steps')
        if not isinstance(steps, list) or any(not isinstance(s, dict) for s in steps):
            errors.append(f'{name}: expected a list of step mappings')
            continue
        for step in steps:
            action = step.get('uses', '')
            if not isinstance(action, str):
                errors.append(f'{name}: invalid uses value')
                continue
            if action and not action.startswith('./') and not re.fullmatch(r'[\w.-]+/[\w./-]+@[0-9a-f]{40}', action):
                errors.append(f'{name}: pin remote action to a commit: {action}')
            runtime = ('python' if action.startswith('actions/setup-python@') else
                       'node' if action.startswith('actions/setup-node@') else None)
            if runtime:
                versions = values(step.get('with', {}).get(f'{runtime}-version'), workflow, job)
                allowed = r'3\.(11|12|13|14|15)(\.\d+)?' if runtime == 'python' else r'(22|24|26)(\.\d+\.\d+)?'
                if not versions or any(not re.fullmatch(allowed, str(v)) for v in versions):
                    errors.append(f'{name}: unsupported or unresolved {runtime} version: {versions}')
    return errors


def check_paths(root):
    errors = []
    for folder in (root / '.github/workflows', root / 'templates/ci'):
        for path in sorted([*folder.glob('*.yml'), *folder.glob('*.yaml')]):
            try:
                problems = check_document(yaml.safe_load(path.read_text()))
            except (ValueError, TypeError, AttributeError, RecursionError, yaml.YAMLError) as exc:
                problems = [f'Invalid or unsupported workflow structure: {exc}']
            errors.extend(f'{path.relative_to(root)}: {problem}' for problem in problems)
    return errors


if __name__ == '__main__':
    problems = check_paths(Path(__file__).resolve().parents[2])
    print('\n'.join(problems) if problems else 'CI workflow/template policy passed')
    raise SystemExit(bool(problems))
