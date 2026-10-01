import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
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
      const fixed = await grade(root, path.join(root, '.agent/fixed'));
      assert.equal(fixed.checks_passed, true, JSON.stringify(fixed));
      assert.equal(fixed.visual_review, 'pending');
      assert.equal(fixed.journeys.length, 2);
      assert.ok(fixed.journeys.every(j => j.captures.length === 4));
    } finally { fs.rmSync(root, {recursive: true, force: true}); }
  });
