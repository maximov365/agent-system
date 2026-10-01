import copy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from tools.profiles.profile import inside, validate
from tools.profiles.readiness import diagnose, probe_http

ROOT = Path(__file__).resolve().parents[1]


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / 'source.py').write_text('print("verified")\n')
        self.data = {'schema_version': 1, 'kinds': ['web'], 'targets': ['browser'],
                     'checks': [{'id': 'journey', 'status': 'configured',
                                 'command': [sys.executable, 'source.py'], 'defined_by': ['source.py']}],
                     'readiness': {'requirements': [{'id': 'python', 'executable': sys.executable,
                                                    'paths': ['source.py'], 'help': 'Install project dependencies.'}],
                                   'model': {'requested': 'gpt-6-astra'},
                                   'launch': {'command': [sys.executable, 'source.py'],
                                              'defined_by': ['source.py'], 'url': 'http://127.0.0.1:4321/',
                                              'expected_text': 'fixture', 'verification_check': 'journey'}}}

    def test_doctor_is_read_only_and_does_not_invent_model_or_runtime_success(self):
        with patch('subprocess.Popen', side_effect=AssertionError('No execution')), \
                patch('http.client.HTTPConnection', side_effect=AssertionError('No network')):
            validate(self.data, self.root)
            result = diagnose(self.data, self.root, inside)
        self.assertEqual(result['status'], 'inspected')
        self.assertFalse(result['commands_executed'])
        self.assertIsNone(result['model']['observed'])
        self.assertEqual(result['journey']['status'], 'not_verified')
        self.assertEqual(result['checks'][0]['result'], 'not_run')
        self.assertEqual(list(self.root.iterdir()), [self.root / 'source.py'])

    def test_missing_executables_and_dependencies_are_actionable_not_false_passes(self):
        self.data['readiness']['requirements'][0]['paths'] = ['node_modules']
        self.data['checks'][0]['command'] = ['./missing-check']
        self.data['readiness']['launch']['command'] = ['./missing-launch']
        validate(self.data, self.root)
        result = diagnose(self.data, self.root, inside)
        self.assertEqual(result['status'], 'attention')
        self.assertEqual(result['requirements'][0]['missing_paths'], ['node_modules'])
        self.assertEqual(result['checks'][0]['status'], 'executable_missing')
        self.assertEqual(result['launch']['status'], 'executable_missing')

    def test_no_readiness_contract_preserves_existing_profiles(self):
        del self.data['readiness']
        validate(self.data, self.root)
        report = diagnose(self.data, self.root, inside)
        self.assertFalse(report['requirements_declared'])
        self.assertEqual(report['launch']['status'], 'not_configured')
        with self.assertRaises(ValueError):
            diagnose(self.data, self.root, inside, probe=True)

    def test_invalid_contracts_and_external_urls_fail_before_execution(self):
        for url in ['file:///index.html', 'https://example.com', 'http://127.0.0.1.evil/',
                    'http://user:secret@localhost/', 'http://0.0.0.0/', 'http://localhost:99999/',
                    'http://localhost/#fragment', 'http://localhost/\n', None]:
            data = copy.deepcopy(self.data); data['readiness']['launch']['url'] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate(data, self.root)
        for change in [{'verification_check': 'unknown'}, {'command': 'python source.py'},
                       {'cwd': '../outside'}, {'defined_by': ['absent.py']}]:
            data = copy.deepcopy(self.data); data['readiness']['launch'].update(change)
            with self.assertRaises(ValueError):
                validate(data, self.root)
        (self.root / 'linked').symlink_to(self.root, target_is_directory=True)
        self.data['readiness']['requirements'][0]['paths'] = ['linked/source.py']
        with self.assertRaises(ValueError):
            validate(self.data, self.root)

    def test_http_identity_failure_and_redirect_do_not_verify_interactions(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                status = 302 if self.path == '/redirect' else 200
                self.send_response(status)
                self.send_header('Location', 'https://example.com/must-not-follow')
                self.end_headers()
                self.wfile.write(b'fixture' if self.path == '/' else b'other application')

            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.addCleanup(server.server_close)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.shutdown)
        for path, expected in [('/', 'responding'), ('/wrong', 'unexpected_response'), ('/redirect', 'unexpected_response')]:
            result = probe_http({'url': f'http://127.0.0.1:{server.server_port}{path}', 'expected_text': 'fixture'})
            self.assertEqual(result['status'], expected)
            self.assertFalse(result['interaction_verified'])

    def test_explicit_verification_records_actual_failure_and_never_visual_approval(self):
        (self.root / 'quality').mkdir()
        (self.root / 'quality/profile.json').write_text(json.dumps(self.data))
        command = [sys.executable, str(ROOT / 'tools/profiles/profile.py'), 'doctor', '--project', str(self.root), '--verify-launch']
        first = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        result = json.loads(first.stdout)
        self.assertTrue(result['commands_executed'])
        self.assertEqual(result['journey']['status'], 'check_passed')
        self.assertEqual(result['visual_review'], 'not_performed')
        evidence = json.loads((Path(result['journey']['evidence']) / 'report.json').read_text())
        self.assertTrue(evidence['executed'])
        self.assertFalse(evidence['reusable'])
        (self.root / 'source.py').write_text('raise SystemExit(3)\n')
        failed = subprocess.run(command, text=True, capture_output=True)
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(json.loads(failed.stdout)['journey']['exit_code'], 3)


if __name__ == '__main__':
    unittest.main()
