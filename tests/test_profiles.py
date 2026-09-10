import copy
from datetime import datetime, timedelta, timezone
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.profiles.profile import validate, run_check, save_report


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / 'check.py').write_text('print("checked")\n')
        self.data = {'schema_version': 1, 'kinds': ['web'], 'targets': ['test browser'],
                     'checks': [{'id': 'unit', 'status': 'configured', 'command': [sys.executable, 'check.py'],
                                 'defined_by': ['check.py'], 'timeout_seconds': 1}]}

    def test_validation_never_runs_and_rejects_false_readiness(self):
        (self.root / 'check.py').write_text('raise RuntimeError("must not run")\n')
        self.assertIs(validate(self.data, self.root), self.data)
        for patch in [{'command': 'echo unsafe'}, {'cwd': '../escape'}, {'defined_by': ['missing.py']},
                      {'status': 'passed'}, {'timeout_seconds': 0}]:
            data = copy.deepcopy(self.data); data['checks'][0].update(patch)
            with self.assertRaises(ValueError):
                validate(data, self.root)
        data = copy.deepcopy(self.data)
        data['checks'] = [{'id': 'device', 'status': 'unavailable', 'reason': 'Device missing'}]
        validate(data, self.root)
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            run_check(data, self.root, 'device', self.root / 'out')
        self.assertFalse((self.root / 'out').exists())

    def test_actual_success_failure_timeout_and_no_overwrite(self):
        result = run_check(self.data, self.root, 'unit', self.root / 'passed')
        self.assertEqual(result['status'], 'passed')
        with self.assertRaises(FileExistsError):
            run_check(self.data, self.root, 'unit', self.root / 'passed')
        (self.root / 'check.py').write_text('raise SystemExit(7)\n')
        self.assertEqual(run_check(self.data, self.root, 'unit', self.root / 'failed')['exit_code'], 7)
        (self.root / 'check.py').write_text('import time; time.sleep(10)\n')
        self.assertEqual(run_check(self.data, self.root, 'unit', self.root / 'timeout')['status'], 'timed_out')
        self.assertEqual(json.loads((self.root / 'timeout/report.json').read_text())['visual_review'], 'not_performed')

    def test_symlinks_duplicate_ids_and_invalid_budgets(self):
        (self.root / 'escape').symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlinked'):
            run_check(self.data, self.root, 'unit', self.root / 'escape/out')
        data = copy.deepcopy(self.data); data['checks'] *= 2
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate(data, self.root)
        data = copy.deepcopy(self.data)
        data['budgets'] = [{'metric': 'p95', 'limit': float('nan'), 'unit': 'ms', 'target': 'phone', 'measurement': 'trace'}]
        with self.assertRaisesRegex(ValueError, 'finite'):
            validate(data, self.root)

    def enable_reuse(self):
        (self.root / 'src').mkdir()
        (self.root / 'src/value.txt').write_text('one')
        (self.root / 'runtime.txt').write_text('runtime dependency')
        self.data['checks'][0]['reuse'] = {
            'deterministic': True, 'side_effect_free': True,
            'dependency_review': 'Synthetic local runner fixture; no application dependencies.',
            'inputs': ['check.py', 'src'], 'runtime_inputs': ['runtime.txt'], 'max_age_seconds': 60}

    def test_navigation_is_a_verified_locator_and_read_only(self):
        self.data['navigation'] = {'source': ['check.py'], 'tests': [], 'references': []}
        validate(self.data, self.root)
        for nav in [{'source': ['missing']}, {'source': ['../escape']}, {'unknown': []}, {'source': 'check.py'}]:
            self.data['navigation'] = nav
            with self.assertRaises(ValueError):
                validate(self.data, self.root)

    def test_reuse_is_explicit_and_does_not_execute_or_renew_evidence(self):
        self.enable_reuse()
        first = run_check(self.data, self.root, 'unit', self.root / 'first', session='task-1')
        self.assertTrue(first['reusable'])
        with patch('tools.profiles.profile.subprocess.Popen', wraps=subprocess.Popen) as execute:
            reused = run_check(self.data, self.root, 'unit', self.root / 'reuse', session='task-1', reuse_from=self.root / 'first')
            execute.assert_not_called()
            self.assertEqual(reused['status'], 'reused')
            self.assertFalse(reused['executed'])
            self.assertFalse(reused['reusable'])
            self.assertEqual(reused['original_finished_at'], first['finished_at'])
            run_check(self.data, self.root, 'unit', self.root / 'fresh', session='task-1', fresh=True)
            self.assertEqual(execute.call_count, 1)
        chained = run_check(self.data, self.root, 'unit', self.root / 'chain', session='task-1', reuse_from=self.root / 'reuse')
        self.assertTrue(chained['executed'])
        with self.assertRaises(ValueError):
            run_check(self.data, self.root, 'unit', self.root / 'invalid', reuse_from=self.root / 'first')

    def test_changed_source_added_deleted_config_runtime_and_session_invalidate(self):
        self.enable_reuse()
        run_check(self.data, self.root, 'unit', self.root / 'first', session='task-1')
        changes = [
            lambda: (self.root / 'src/value.txt').write_text('two'),
            lambda: (self.root / 'src/new.txt').write_text('new'),
            lambda: (self.root / 'src/value.txt').unlink(),
            lambda: self.data['checks'][0].update(timeout_seconds=2),
            lambda: (self.root / 'runtime.txt').write_text('updated'),
            lambda: (self.root / 'check.py').write_text('print("updated tests")\n'),
        ]
        for i, change in enumerate(changes):
            original = self.root / f'before-{i}'
            run_check(self.data, self.root, 'unit', original, session='task-1')
            change()
            result = run_check(self.data, self.root, 'unit', self.root / f'after-{i}', session='task-1', reuse_from=original)
            self.assertTrue(result['executed'])
        result = run_check(self.data, self.root, 'unit', self.root / 'session', session='task-2', reuse_from=self.root / 'after-5')
        self.assertTrue(result['executed'])

    def test_environment_change_invalidates_without_persisting_values(self):
        self.enable_reuse()
        with patch.dict(os.environ, {'QUALITY_TEST_PRIVATE': 'private-value-one'}):
            run_check(self.data, self.root, 'unit', self.root / 'first', session='task-1')
        with patch.dict(os.environ, {'QUALITY_TEST_PRIVATE': 'private-value-two'}):
            result = run_check(self.data, self.root, 'unit', self.root / 'second', session='task-1', reuse_from=self.root / 'first')
        self.assertTrue(result['executed'])
        for folder in ['first', 'second']:
            self.assertNotIn('private-value', (self.root / folder / 'report.json').read_text())

    @unittest.skipUnless(os.name == 'posix', 'Executable fixture uses a POSIX shebang')
    def test_resolved_executable_contents_and_path_resolution_invalidate(self):
        self.enable_reuse()
        executable = self.root / 'verify'
        executable.write_text('#!/bin/sh\nprintf first\n'); executable.chmod(0o755)
        self.data['checks'][0]['command'] = ['./verify']
        first = run_check(self.data, self.root, 'unit', self.root / 'first', session='task-1')
        self.assertTrue(first['reusable'])
        executable.write_text('#!/bin/sh\nprintf second\n')
        second = run_check(self.data, self.root, 'unit', self.root / 'second', session='task-1', reuse_from=self.root / 'first')
        self.assertTrue(second['executed'])
        self.assertEqual((self.root / 'second/output.log').read_text(), 'second')

    def test_failed_expired_future_and_corrupt_evidence_never_reused(self):
        self.enable_reuse()
        for i, change in enumerate([
            lambda r: r.update(status='failed'),
            lambda r: r.update(finished_at=(datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()),
            lambda r: r.update(finished_at=(datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()),
            lambda r: r.update(fingerprint='wrong'),
        ]):
            original = self.root / f'original-{i}'
            report = run_check(self.data, self.root, 'unit', original, session='task-1')
            change(report); save_report(original, report)
            result = run_check(self.data, self.root, 'unit', self.root / f'retry-{i}', session='task-1', reuse_from=original)
            self.assertTrue(result['executed'])
        for i, filename in enumerate(['report.json', 'output.log', 'report.sha256']):
            original = self.root / f'corrupt-{i}'
            run_check(self.data, self.root, 'unit', original, session='task-1')
            (original / filename).write_text('corrupted')
            self.assertTrue(run_check(self.data, self.root, 'unit', self.root / f'corrupt-retry-{i}', session='task-1', reuse_from=original)['executed'])

    def test_midrun_changes_missing_and_symlink_inputs_disable_reuse(self):
        self.enable_reuse()
        (self.root / 'check.py').write_text('from pathlib import Path\nPath("src/value.txt").write_text("changed")\n')
        result = run_check(self.data, self.root, 'unit', self.root / 'changed', session='task-1')
        self.assertEqual(result['status'], 'passed')
        self.assertFalse(result['reusable'])
        (self.root / 'src/link').symlink_to(self.root / 'check.py')
        result = run_check(self.data, self.root, 'unit', self.root / 'symlink', session='task-1')
        self.assertTrue(result['executed'])
        self.assertFalse(result['reusable'])
        self.assertIn('Symlink', result['reuse_note'])
        (self.root / 'src/link').unlink()
        (self.root / 'runtime.txt').unlink()
        self.assertFalse(run_check(self.data, self.root, 'unit', self.root / 'missing', session='task-1')['reusable'])

    def test_policy_and_hash_budget_fail_closed(self):
        self.enable_reuse()
        for update in [{'deterministic': False}, {'side_effect_free': False}, {'inputs': []},
                       {'max_age_seconds': 901}, {'dependency_review': ''}]:
            data = copy.deepcopy(self.data); data['checks'][0]['reuse'].update(update)
            with self.assertRaises(ValueError):
                validate(data, self.root)
        with patch('tools.profiles.profile.MAX_INPUT_BYTES', 1):
            result = run_check(self.data, self.root, 'unit', self.root / 'large', session='task-1')
        self.assertTrue(result['executed'])
        self.assertFalse(result['reusable'])
