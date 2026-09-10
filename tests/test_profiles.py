import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from tools.profiles.profile import validate, run_check


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
