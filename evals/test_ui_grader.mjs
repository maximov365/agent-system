import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {grade} from './graders/ui-filter.mjs';

test('UI grader rejects broken search, missing clear action and form reload; accepts working controls',
  {skip: process.env.AGENT_VISUAL_TEST_BROWSER !== '1'}, async () => {
    const root = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'eval-ui-'));
    try {
      fs.cpSync(new URL('./fixtures/ui-filter', import.meta.url), root, {recursive: true});
      const broken = await grade(root, path.join(root, '.agent/broken'));
      assert.equal(broken.checks_passed, false);
      fs.writeFileSync(path.join(root, 'filter.mjs'), `export function filterItems(items, query = '') {
        return items.filter(item => item.name.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()));
      }`);
      const missingControls = await grade(root, path.join(root, '.agent/missing-controls'));
      assert.equal(missingControls.checks_passed, false);
      fs.appendFileSync(path.join(root, 'app.mjs'), `
        document.querySelector('form').addEventListener('submit', event => event.preventDefault());
        document.querySelector('#clear').addEventListener('click', () => {input.value=''; render(); input.focus();});
      `);
      // Exercise the paired runner's isolated grader and explicit dependency path.
      const snapshot = path.join(root, '.agent/grading-snapshot');
      for (const relative of ['evals/graders/ui-filter.mjs', 'tools/visual/run.mjs',
        'tools/visual/package.json', 'tools/visual/package-lock.json']) {
        const destination = path.join(snapshot, relative);
        fs.mkdirSync(path.dirname(destination), {recursive: true});
        fs.copyFileSync(new URL(`../${relative}`, import.meta.url), destination);
      }
      const fixedOutput = path.join(root, '.agent/fixed');
      const result = JSON.parse(execFileSync(process.execPath,
        [path.join(snapshot, 'evals/graders/ui-filter.mjs'), root, fixedOutput],
        {encoding: 'utf8', timeout: 60_000, env: {...process.env,
          AGENT_NODE_MODULES: process.env.AGENT_NODE_MODULES ||
            fileURLToPath(new URL('../tools/visual/node_modules', import.meta.url))}}));
      assert.equal(result.checks_passed, true);
      const fixed = JSON.parse(fs.readFileSync(path.join(fixedOutput, 'report.json'), 'utf8'));
      assert.equal(fixed.checks_passed, true, JSON.stringify(fixed));
      assert.equal(fixed.visual_review, 'pending');
      assert.equal(fixed.journeys.length, 2);
      assert.ok(fixed.journeys.every(j => j.captures.length === 4));
    } finally { fs.rmSync(root, {recursive: true, force: true}); }
  });
