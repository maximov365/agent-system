import copy
from pathlib import Path
import tempfile
import unittest

from tools.ci.check import check_document, check_paths


class CIPolicyTests(unittest.TestCase):
    def valid(self):
        return {'permissions': {'contents': 'read'}, 'jobs': {'test': {
            'runs-on': 'ubuntu-24.04', 'timeout-minutes': 15,
            'steps': [{'uses': 'actions/setup-node@' + 'a' * 40,
                       'with': {'node-version': '24'}}]}}}

    def test_current_workflows_and_templates(self):
        self.assertEqual(check_paths(Path(__file__).resolve().parents[1]), [])

    def test_rejects_old_template_runtime_actions_and_runner(self):
        doc = self.valid()
        job = doc['jobs']['test']
        job['runs-on'] = 'ubuntu-latest'
        job['steps'][0] = {'uses': 'actions/setup-node@v4', 'with': {'node-version': '20'}}
        errors = check_document(doc)
        self.assertTrue(any('runner' in e for e in errors))
        self.assertTrue(any('pin remote' in e for e in errors))
        self.assertTrue(any('node version' in e for e in errors))

    def test_permissions_timeout_and_unresolved_versions_fail(self):
        for change, message in [('permissions', 'permissions'), ('timeout', 'timeout'), ('version', 'version')]:
            doc = self.valid()
            if change == 'permissions': doc['permissions'] = 'write-all'
            if change == 'timeout': doc['jobs']['test']['timeout-minutes'] = 0
            if change == 'version': doc['jobs']['test']['steps'][0]['with']['node-version'] = '${{ secrets.VERSION }}'
            self.assertTrue(any(message in e for e in check_document(doc)))

    def test_matrix_and_dispatch_options_are_all_checked(self):
        doc = self.valid()
        job = doc['jobs']['test']
        job['strategy'] = {'matrix': {'node': ['22', "${{ inputs.node || '24' }}"]}}
        job['steps'][0]['with']['node-version'] = '${{ matrix.node }}'
        doc[True] = {'workflow_dispatch': {'inputs': {'node': {'options': ['24', '26']}}}}
        self.assertEqual(check_document(doc), [])
        broken = copy.deepcopy(doc)
        broken[True]['workflow_dispatch']['inputs']['node']['options'].append('20')
        self.assertTrue(any('node version' in e for e in check_document(broken)))

    def test_malformed_yaml_is_a_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'templates/ci').mkdir(parents=True)
            (root / 'templates/ci/bad.yml').write_text('jobs: [invalid')
            self.assertTrue(check_paths(root))
        self.assertTrue(check_document({'jobs': []}))


if __name__ == '__main__':
    unittest.main()
