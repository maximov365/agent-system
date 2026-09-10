#!/usr/bin/env python3
"""Explicit opt-in, bounded paired Codex evaluation using synthetic fixtures only."""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import setup
from sync import is_template


def digest(files):
    h = hashlib.sha256()
    for name, data in sorted(files.items()):
        h.update(name.encode() + b'\0' + data + b'\0')
    return h.hexdigest()


def invoke(argv, cwd, timeout, input_text=None):
    process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = process.communicate(input_text, timeout=timeout)
        return process.returncode, out, err
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        out, err = process.communicate()
        return 124, out, err


def framework_files(root):
    """Load this trusted repository revision's own manifest, not today's ownership."""
    namespace = {'__name__': 'eval_framework_manifest'}
    exec(compile((root/'framework_manifest.py').read_text(), 'framework_manifest.py', 'exec'), namespace)
    return {str(dst): source.read_bytes() for dst, source in namespace['deployment_sources'](root).items()}


def baseline_files(ref):
    revision = subprocess.check_output(['git', 'rev-parse', '--verify', ref + '^{commit}'], cwd=ROOT, text=True).strip()
    archive = subprocess.check_output(['git', 'archive', revision], cwd=ROOT)
    with tempfile.TemporaryDirectory(prefix='agent-system-eval-baseline-') as folder:
        root = Path(folder)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            for member in tar.getmembers():
                relative = Path(member.name)
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('Unsafe archive path')
                if member.isfile():
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(tar.extractfile(member).read())
                elif not member.isdir():
                    raise ValueError('Baseline archive contains a non-regular entry')
        return revision, framework_files(root)


def render_snapshot(files, config):
    rendered = {}
    for rel, data in files.items():
        # Keep canonical raw templates intact so downstream reconfiguration still works.
        if is_template(Path(rel)) and setup.has_variables(data.decode()):
            data = setup.render_text(data.decode(), config).encode()
        rendered[rel] = data
    return rendered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', required=True)
    parser.add_argument('--model', default='gpt-6-astra')
    parser.add_argument('--effort', default='medium')
    parser.add_argument('--repeats', type=int, default=2, choices=range(1, 4))
    parser.add_argument('--timeout', type=int, default=240, choices=range(30, 601))
    parser.add_argument('--output', required=True)
    parser.add_argument('--baseline-ref', help='Compare a trusted git revision against the current framework instead of plain')
    parser.add_argument('--run', action='store_true', help='Authorize actual model calls; otherwise only validate fixtures')
    args = parser.parse_args()
    fixtures = {}
    for name in ['pagination', 'authorization']:
        fixtures[name] = {str(p.relative_to(ROOT/'evals/fixtures'/name)): p.read_bytes()
                          for p in (ROOT/'evals/fixtures'/name).rglob('*') if p.is_file()}
    framework = framework_files(ROOT)
    before_revision, before_files = baseline_files(args.baseline_ref) if args.baseline_ref else (None, {})
    conditions = ['baseline', 'candidate'] if args.baseline_ref else ['plain', 'framework']
    snapshots = dict(zip(conditions, [before_files, framework]))
    config = setup.load_config(ROOT/'project.config.yaml')
    rendered = {name: render_snapshot(files, config) for name, files in snapshots.items()}
    metadata = {'schema_version': 1, 'date': datetime.now(timezone.utc).isoformat(),
                'model_requested': args.model, 'model_resolved': None, 'reasoning_effort': args.effort,
                'framework_base_revision': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'framework_snapshot_sha256': digest(framework),
                'baseline_revision': before_revision,
                'condition_sha256': {name: digest(files) for name, files in snapshots.items()},
                'rendered_condition_sha256': {name: digest(files) for name, files in rendered.items()},
                'entry_words': {name: len(files.get('AGENTS.md', b'').split()) for name, files in rendered.items()},
                'fixture_sha256': {name:digest(files) for name,files in fixtures.items()},
                'grader_sha256': {name:hashlib.sha256((ROOT/'evals/graders'/f'{name}.py').read_bytes()).hexdigest() for name in fixtures},
                'repeats': args.repeats, 'runs': [], 'cost_usd': None,
                'limitations': ['Synthetic Python tasks only; no visual/game model comparison.',
                  'Requested model recorded; CLI JSON may not expose independently resolved model identity.',
                  'User config disabled; host built-in instructions/tools still apply to both conditions.',
                  'No independent reviewer. Subscription token counts are not API dollar cost.']}
    if not args.run:
        print(json.dumps({**metadata,'executed':False},indent=2));return 0
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    metadata['runtime'] = subprocess.check_output([args.codex,'--version'],text=True).strip()
    # Separate temporary root avoids inheriting framework AGENTS.md in baseline.
    root = Path(tempfile.mkdtemp(prefix='agent-system-paired-')).resolve()
    metadata['local_workspace'] = str(root)
    for condition, files in rendered.items():
        snapshot = root/f'{condition}-snapshot';snapshot.mkdir()
        for rel, data in files.items():
            target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
    for repeat in range(args.repeats):
        for task,files in fixtures.items():
            order=conditions if repeat%2==0 else list(reversed(conditions))
            for condition in order:
                run_id=f'{task}-{condition}-{repeat+1}';work=root/run_id
                shutil.copytree(root/f'{condition}-snapshot',work)
                for rel,data in files.items():(work/rel).write_bytes(data)
                subprocess.run(['git','init','-q',str(work)],check=True)
                prompt=(work/'task.txt').read_text()
                argv=[args.codex,'exec','--ephemeral','--ignore-user-config','--sandbox','workspace-write',
                      '--model',args.model,'-c',f'model_reasoning_effort="{args.effort}"','--json','-C',str(work),'-']
                start=time.monotonic();code,out,err=invoke(argv,work,args.timeout,prompt)
                record={'run_id':run_id,'task':task,'condition':condition,'repeat':repeat+1,
                        'elapsed_seconds':round(time.monotonic()-start,3),'exit_code':code,'usage':None,
                        'manual_interventions':0,'independent_review':False,'checks':{},'model_completed':False}
                messages=[];commands=[];output_chars=0
                for line in out.splitlines():
                    try:event=json.loads(line)
                    except json.JSONDecodeError:continue
                    if event.get('type')=='turn.completed':record['usage']=event.get('usage');record['model_completed']=True
                    item=event.get('item',{})
                    if event.get('type')=='item.completed' and item.get('type')=='agent_message':messages.append(item.get('text',''))
                    if event.get('type')=='item.completed' and item.get('type')=='command_execution':
                        commands.append(item.get('command',''))
                        output_chars += len(item.get('aggregated_output',''))
                # Only generated synthetic outputs are saved locally, never private sessions.
                folder=output/run_id;folder.mkdir()
                (folder/'events.jsonl').write_text(out);(folder/'stderr.log').write_text(err)
                (folder/'final.txt').write_text('\n'.join(messages))
                if (work/'core.py').is_file():shutil.copyfile(work/'core.py',folder/'core.py')
                for label,command in [('public',[sys.executable,'-m','unittest','discover','-v']),
                                      ('held_out',[sys.executable,str(ROOT/'evals/graders'/f'{task}.py'),str(work)])]:
                    rc,stdout,stderr=invoke(command,work,30)
                    record['checks'][label]={'passed':rc==0,'exit_code':rc}
                    (folder/f'{label}.log').write_text(stdout+stderr)
                record['observed_command_count']=len(commands)
                record['observed_command_output_chars']=output_chars
                record['passed']=code==0 and record['model_completed'] and all(c['passed'] for c in record['checks'].values())
                metadata['runs'].append(record)
                (output/'report.json').write_text(json.dumps(metadata,indent=2)+'\n')
                print(json.dumps(record),flush=True)
                if not record['model_completed']:
                    print('Stopping: runtime did not complete; inspect local errors.',flush=True)
                    return 2
    return 0 if all(r['passed'] for r in metadata['runs']) else 1


if __name__=='__main__':raise SystemExit(main())
