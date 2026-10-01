import unittest
import subprocess
import sys
import tempfile
from pathlib import Path

from evals.run_paired import ROOT, baseline_files, digest, framework_files, render_snapshot, fixture_files, write_files
import setup


class EvaluationTests(unittest.TestCase):
    def test_nested_fixture_and_multifile_grader(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_files(root, fixture_files('multifile'))
            def grade():
                return subprocess.run([sys.executable, '-B', str(ROOT / 'evals/graders/multifile.py'), folder],
                                      capture_output=True, text=True)
            self.assertNotEqual(grade().returncode, 0)
            (root / 'catalog/query.py').write_text('def matching(items, query):\n return [dict(x) for x in items if query.strip().casefold() in x["title"].casefold()]\n')
            (root / 'catalog/service.py').write_text('from .query import matching\ndef search(items, query="", offset=0, limit=20):\n rows=matching(items, query)\n start=max(0, offset)\n return {"items":rows[start:start+max(0,limit)],"total":len(rows)}\n')
            (root / 'catalog/api.py').write_text('from .service import search\ndef number(value):\n if isinstance(value,bool) or not isinstance(value,(int,str)): raise ValueError("integer required")\n return int(value)\ndef handle(items, params):\n return search(items,params.get("q",""),number(params.get("offset",0)),number(params.get("limit",20)))\n')
            result = grade()
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_canonical_templates_remain_raw_and_active_entry_is_rendered(self):
        files = framework_files(ROOT)
        rendered = render_snapshot(files, setup.load_config(ROOT / 'project.config.yaml'))
        self.assertFalse(setup.has_variables(rendered['AGENTS.md'].decode()))
        raw = '.agent-system/templates/AGENTS.md'
        self.assertEqual(rendered[raw], files[raw])
        self.assertTrue(setup.has_variables(rendered[raw].decode()))
        self.assertNotIn('quality/profile.json', files)
        self.assertFalse(any(Path(p).parts[0] in {'.git', '.agent', '.codex', 'examples'} for p in files))

    def test_revision_snapshot_uses_its_own_manifest(self):
        # HEAD is trusted repository code. This makes no model or network call.
        revision, files = baseline_files('HEAD')
        self.assertEqual(len(revision), 40)
        self.assertIn('AGENTS.md', files)
        self.assertEqual(digest(files), digest(dict(reversed(list(files.items())))))
