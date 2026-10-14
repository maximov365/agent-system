import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import net from 'node:net';
import crypto from 'node:crypto';
import {run, validateConfig, inside} from '../run.mjs';

const base = () => ({schema_version: 1, baseURL: 'http://127.0.0.1:4319',
  viewports: [{name: 'small', width: 390, height: 600}],
  journeys: [{id: 'main', steps: [{type: 'capture', name: 'screen'}]}]});

test('preflight rejects remote URLs, escaping paths and missing capture', () => {
  const root = fs.realpathSync(os.tmpdir());
  assert.throws(() => validateConfig({...base(), baseURL: 'https://example.com'}, root), /local URL/);
  assert.throws(() => inside(root, '../outside'), /escapes/);
  const config = base(); config.journeys[0].steps = [{type: 'click', selector: 'button'}];
  assert.throws(() => validateConfig(config, root), /capture at least one/);
});

test('preflight refuses shell commands and duplicate evidence names', () => {
  const root = fs.realpathSync(os.tmpdir());
  assert.throws(() => validateConfig({...base(), server: {command: 'echo unsafe'}}, root), /argv/);
  const config = base(); config.journeys[0].steps.push({type: 'capture', name: 'screen'});
  assert.throws(() => validateConfig(config, root), /duplicate capture/);
});

test('preflight refuses symlinked output parent', () => {
  const root = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'visual-path-'));
  try {
    fs.symlinkSync(os.tmpdir(), path.join(root, 'escape'));
    assert.throws(() => inside(root, 'escape/result'), /Symlinked/);
  } finally { fs.rmSync(root, {recursive: true, force: true}); }
});

test('preflight rejects unsupported touch, coordinates and recording options', () => {
  const config = base();
  config.journeys[0].steps.unshift({type: 'tap', x: 40, y: 40});
  assert.throws(() => validateConfig(config, os.tmpdir()), /touch-enabled/);
  config.viewports[0].touch = true;
  validateConfig(config, os.tmpdir());
  for (const x of [-1, 390, NaN, '20']) {
    config.journeys[0].steps[0].x = x;
    assert.throws(() => validateConfig(config, os.tmpdir()), /coordinates/);
  }
  for (const options of [{video: 'true'}, {videoFps: 30}, {video: true, videoFps: 61},
    {video: true, videoFps: 2.5}, {timeoutMs: 0}, {timeoutMs: 60001}]) {
    assert.throws(() => validateConfig({...base(), ...options}, os.tmpdir()));
  }
});

test('real browser: touch-only input, async assertions, motion videos and negative cases',
  {skip: process.env.AGENT_VISUAL_TEST_BROWSER !== '1'}, async () => {
    const root = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'visual-touch-'));
    const socket = net.createServer();
    await new Promise(resolve => socket.listen(0, '127.0.0.1', resolve));
    const port = socket.address().port;
    await new Promise(resolve => socket.close(resolve));
    try {
      fs.writeFileSync(path.join(root, 'server.mjs'), `import http from 'node:http';
        http.createServer((req,res)=>{res.setHeader('Content-Type','text/html');
        res.end(\`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
        <style>button{position:absolute;left:0;top:0;width:200px;height:120px}</style>
        <button>Start</button><output>Waiting</output><ul></ul><script>
        const state={pointerType:'none',touchStarts:0};
        const button=document.querySelector('button');
        button.addEventListener('pointerdown',e=>state.pointerType=e.pointerType);
        button.addEventListener('touchstart',()=>{if(location.pathname==='/broken')return;
          state.touchStarts++;setTimeout(()=>document.querySelector('output').textContent='Touched',90)});
        button.addEventListener('keydown',e=>{if(e.key==='Enter')setTimeout(()=>{
          document.querySelector('ul').innerHTML='<li>Keyboard works</li>'},90)});
        window.__agentEvidence={snapshot:()=>({...state,motion:matchMedia('(prefers-reduced-motion: reduce)').matches})};
        </script>\`)}).listen(${port},'127.0.0.1');`);
      const config = {...base(), baseURL: `http://127.0.0.1:${port}`, timeoutMs: 700,
        video: true, videoFps: 60, reducedMotion: 'no-preference',
        viewports: [{name: 'mobile', width: 390, height: 600, mobile: true}],
        server: {command: [process.execPath, 'server.mjs']},
        journeys: [{id: 'input', steps: [
          {type: 'tap', x: 50, y: 50},
          {type: 'expectText', selector: 'output', contains: 'Touched'},
          {type: 'tap', role: 'button', name: 'Start'},
          {type: 'press', selector: 'button', key: 'Enter'},
          {type: 'expectCount', selector: 'li', count: 1},
          {type: 'probe', equals: {pointerType: 'touch', touchStarts: 2, motion: false}},
          {type: 'capture', name: 'complete'}]}]};
      const output = path.join(root, 'normal');
      const success = await run(config, {project: root, output});
      assert.equal(success.checks_passed, true, JSON.stringify(success));
      const journey = success.journeys[0], recording = journey.recordings[0];
      assert.equal(journey.touch_enabled, true);
      assert.equal(journey.reduced_motion, 'no-preference');
      assert.equal(journey.captures[0].animations, 'allow');
      assert.equal(recording.fps_requested, 60);
      assert.equal(recording.fps_observed, null);
      assert.equal(recording.review, 'pending');
      const bytes = fs.readFileSync(path.join(output, recording.file));
      assert.ok(bytes.length > 1000);
      assert.equal(recording.sha256, crypto.createHash('sha256').update(bytes).digest('hex'));
      const html = fs.readFileSync(path.join(output, 'index.html'), 'utf8');
      assert.ok(html.includes('<video controls') && html.includes(recording.file));
      const reduced = structuredClone(config);
      reduced.reducedMotion = 'reduce';
      reduced.journeys[0].steps.find(s => s.type === 'probe').equals.motion = true;
      const reducedReport = await run(reduced, {project: root, output: path.join(root, 'reduced')});
      assert.equal(reducedReport.checks_passed, true, JSON.stringify(reducedReport));
      assert.equal(reducedReport.journeys[0].captures[0].animations, 'disabled');
      const broken = structuredClone(config); broken.journeys[0].route = '/broken';
      const failed = await run(broken, {project: root, output: path.join(root, 'broken')});
      assert.equal(failed.checks_passed, false);
      assert.match(failed.journeys[0].errors.join(' '), /Expected visible text.*Touched/);
      assert.equal(failed.journeys[0].recordings.length, 1);
      const absent = structuredClone(config);
      absent.journeys[0].steps = [{type: 'expectCount', selector: 'li', count: 2}, {type: 'capture', name: 'missing'}];
      const missing = await run(absent, {project: root, output: path.join(root, 'missing')});
      assert.equal(missing.checks_passed, false);
      assert.match(missing.journeys[0].errors.join(' '), /Expected 2 elements, got 0/);
    } finally { fs.rmSync(root, {recursive: true, force: true}); }
  });

test('real browser: interactions, capture, error detection, baseline mismatch and cleanup',
  {skip: process.env.AGENT_VISUAL_TEST_BROWSER !== '1'}, async () => {
    const root = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'visual-e2e-'));
    const socket = net.createServer();
    await new Promise(resolve => socket.listen(0, '127.0.0.1', resolve));
    const port = socket.address().port;
    await new Promise(resolve => socket.close(resolve));
    try {
      fs.writeFileSync(path.join(root, 'server.mjs'), `import http from 'node:http';
        http.createServer((req,res)=>{res.setHeader('Content-Type','text/html');
        res.end('<html><body><button onclick="this.textContent=\\'Done\\'">Start</button>'+
        (req.url.includes('broken')?'<script>throw Error("Intentional browser error")</script>':'')+'</body></html>')
        }).listen(${port},'127.0.0.1');`);
      const config = {...base(), baseURL: `http://127.0.0.1:${port}`,
        server: {command: [process.execPath, 'server.mjs']}};
      config.journeys[0].steps.unshift({type: 'click', role: 'button', name: 'Start'},
        {type: 'expectText', selector: 'button', contains: 'Done'});
      const success = await run(config, {project: root, output: path.join(root, 'success')});
      assert.equal(success.checks_passed, true, JSON.stringify(success));
      assert.equal(success.visual_review, 'pending');
      const capture = success.journeys[0].captures[0];
      assert.equal(capture.sha256.length, 64);
      assert.equal(fs.existsSync(path.join(root, 'success', capture.file)), true);
      assert.equal(fs.existsSync(path.join(root, 'success/small--main--trace.zip')), true);
      const broken = structuredClone(config); broken.journeys[0].route = '/broken';
      const failure = await run(broken, {project: root, output: path.join(root, 'failure')});
      assert.equal(failure.checks_passed, false);
      assert.match(failure.journeys[0].errors.join(' '), /Intentional browser error/);
      fs.mkdirSync(path.join(root, 'baselines'));
      fs.copyFileSync(path.join(root, 'success', capture.file), path.join(root, 'baselines', capture.file));
      const changed = structuredClone(config); changed.baselineDir = 'baselines';
      changed.maxDiffRatio = 0;
      changed.journeys[0].steps = [{type: 'capture', name: 'screen'}];
      const diff = await run(changed, {project: root, output: path.join(root, 'diff')});
      assert.equal(diff.checks_passed, false);
      assert.match(diff.journeys[0].errors.join(' '), /Visual baseline changed/);
      assert.equal(fs.existsSync(path.join(root, 'diff', capture.file.replace('.png', '--diff.png'))), true);
      // Every run starts its own server on the same port: a leaked process breaks the next run.
    } finally { fs.rmSync(root, {recursive: true, force: true}); }
  });
