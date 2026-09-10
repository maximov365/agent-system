import unittest
from pathlib import Path

from evals.run_paired import ROOT, baseline_files, digest, framework_files, render_snapshot
import setup


class EvaluationTests(unittest.TestCase):
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
