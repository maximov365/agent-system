import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import net from 'node:net';
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
