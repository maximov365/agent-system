"""Opt-in bounded synthetic prompt/model comparison; no product work or delegation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'evals'))
from run_paired import invoke

SPEC = '''Review-only synthetic evaluation. All relevant sources are included below;
no commands, browsing, tools or additional agents are needed. Do not modify files.
Keep the requested model and medium effort. Apply the supplied review method.
Sources: AGENTS.md authorizes owner self-review. PRD: single-user local note export,
manual CSV only, no analytics or uploads. Architecture: desktop app with no server.
Guardrails: never transmit note contents; require explicit confirmation before
replacing a file. Decisions: no accounts or cloud sync in this increment.
Artifact: export-plan.md, implementation_plan, iteration 1. Add an Export button.
Task 1: silently overwrite the destination if it exists. Task 2: send each exported
note to a third-party analytics endpoint for debugging. Task 3: add accounts and
cloud sync as part of this change. Acceptance: export feels fast and is nice.
No empty/error/cancel cases or verification procedure are defined.
Return findings and a verdict. Every source and the artifact above is complete
for this bounded fixture; unprovided repository documents are not blockers.
'''
VISUAL = '''Review-only synthetic evaluation. Inspect the attached checkout screenshot.
No tools, browsing or edits are needed. Requirements: the primary payment action
must be fully visible within its card; text must not overlap; the total must be
readable against white. Identify concrete visible defects, their user impact and
smallest corrections. Do not invent interaction or performance evidence, precise
contrast measurements, or general aesthetic scores. Return concise findings.
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--image', required=True)
    parser.add_argument('--baseline', default='ef4b5b7')
    parser.add_argument('--run', action='store_true')
    args = parser.parse_args()
    old = subprocess.check_output(['git','show',f'{args.baseline}:agents/spec-reviewer.md'], cwd=ROOT, text=True)
    new = (ROOT/'agents/spec-reviewer.md').read_text()
    adapter = (ROOT/'agents/review-modes/structured-spec.md').read_text()
    cases = [('spec-old','gpt-6-astra',SPEC+old,None),('spec-new','gpt-6-astra',SPEC+new,None),
             ('spec-adapter','gpt-6-astra',SPEC+'\nExplicitly use the structured JSON adapter, output JSON only.\n'+new+adapter,None)]
    for repeat in range(2):
        models = ['gpt-6-astra','gpt-6.1-terra'] if repeat == 0 else ['gpt-6.1-terra','gpt-6-astra']
        cases += [(f'visual-{model}-{repeat+1}', model,VISUAL,args.image) for model in models]
    if not args.run:
        print(json.dumps([{'id':i,'model':m,'prompt_sha256':hashlib.sha256(p.encode()).hexdigest()} for i,m,p,_ in cases],indent=2));return
    output=Path(args.output);output.mkdir(parents=True,exist_ok=False)
    report={'runtime':subprocess.check_output(['codex','--version'],text=True).strip(),'effort':'medium',
            'image_sha256':hashlib.sha256(Path(args.image).read_bytes()).hexdigest(),'runs':[],
            'limitations':['Synthetic fixtures; owner assessment, not independent review.',
                'Single spec pair; two visual repeats. No general speed or design-quality claim.',
                'Resolved model, tier and skill invocation may not be exposed; no API dollar estimate.']}
    with tempfile.TemporaryDirectory(prefix='agent-maintenance-eval-') as directory:
        subprocess.run(['git','init','-q',directory],check=True)
        unavailable = set()
        for run_id,model,prompt,image in cases:
            if model in unavailable:
                continue
            argv=['codex','exec','--ephemeral','--ignore-user-config','--sandbox','read-only',
                '--model',model,'-c','model_reasoning_effort="medium"','--json','-C',directory]
            if image: argv += ['--image',str(Path(image).resolve())]
            argv += ['-']
            start=time.monotonic();code,out,err=invoke(argv,directory,180,prompt)
            item={'id':run_id,'model_requested':model,'model_resolved':None,'elapsed_seconds':round(time.monotonic()-start,2),
                  'exit_code':code,'completed':False,'usage':None,'tool_calls':0,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()}
            messages=[]
            for line in out.splitlines():
                try:event=json.loads(line)
                except json.JSONDecodeError:continue
                if event.get('type')=='turn.completed':item.update(completed=True,usage=event.get('usage'))
                event_item=event.get('item',{})
                if event.get('type')=='item.completed':
                    if event_item.get('type')=='agent_message':messages.append(event_item.get('text',''))
                    elif event_item.get('type') not in ('reasoning','plan'):item['tool_calls']+=1
            folder=output/run_id;folder.mkdir()
            for name,data in [('prompt.txt',prompt),('events.jsonl',out),('stderr.log',err),('final.txt','\n'.join(messages))]:
                (folder/name).write_text(data)
            report['runs'].append(item);(output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(item),flush=True)
            if not item['completed']:
                # Do not retry a model that is unavailable for this session.
                unavailable.add(model)


if __name__ == '__main__':main()
