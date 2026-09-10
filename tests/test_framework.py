"""Regression tests for real sync, rendering, bootstrap, and audit hazards."""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import audit
import setup
import sync
import metrics
import metrics_workflow
from framework_manifest import deployment_sources, seed_sources, is_framework_change

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bootstrap", ROOT / "init-downstream.py")
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)
hook_spec = importlib.util.spec_from_file_location("hook_installer", ROOT / "hooks/install.py")
hook_installer = importlib.util.module_from_spec(hook_spec)
hook_spec.loader.exec_module(hook_installer)


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


class FrameworkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / "project"
        self.project.mkdir()
        (self.project / "project.config.yaml").write_text('project:\n  name: "Trial Project"\n')

    def sync(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return sync.cmd_sync(self.project, **kwargs)

    def command(self, *args):
        return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, text=True, capture_output=True)

    def test_preview_with_render_has_no_writes(self):
        for option in ["--dry-run", "--diff"]:
            before = snapshot(self.project)
            result = self.command(ROOT / "sync.py", "--target", self.project, "--render", option)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(snapshot(self.project), before)
            if option == "--diff":
                self.assertIn("Trial Project", result.stdout)
                self.assertIn("+# Agent System — Trial Project", result.stdout)
                rendered_diff = result.stdout.split("+++ new/AGENTS.md\n", 1)[1].split("--- old/", 1)[0]
                self.assertNotIn("+# Agent System — {{ project.name }}", rendered_diff)

    def test_all_diff_honors_preview(self):
        before = snapshot(self.project)
        with patch.object(sys, "argv", ["sync.py", "--all", "--diff", "--render"]), patch.object(sync, "load_downstream_projects", return_value=[self.project]), contextlib.redirect_stdout(io.StringIO()) as out:
            sync.main()
        self.assertEqual(snapshot(self.project), before)
        self.assertIn("+++ new/AGENTS.md", out.getvalue())

    def test_ownership_has_no_overlap_or_app_setup_collision(self):
        framework, seeds = deployment_sources(ROOT), seed_sources(ROOT)
        self.assertFalse(framework.keys() & seeds.keys())
        self.assertNotIn(Path("setup.py"), framework)
        self.assertNotIn(Path(".github/workflows/agent-quality.yml"), framework)
        self.assertNotIn(Path(".github/workflows/agent-quality.yml"), seeds)
        self.assertIn(Path(".agent-system/setup.py"), framework)
        self.assertTrue(is_framework_change("agents/deleted-role.md"))
        self.assertFalse(is_framework_change("docs/TASKS.md"))
        self.assertFalse(is_framework_change("docs/DECISIONS.md"))
        self.assertTrue(is_framework_change("agents/discovery-modes/deleted-mode.md"))
        self.assertIn(Path("AGENTS.md"), deployment_sources(self.base))

    def test_examples_and_optional_dependencies_never_ship_to_projects(self):
        sources = deployment_sources(ROOT) | seed_sources(ROOT)
        self.assertFalse(any("examples" in source.relative_to(ROOT).parts for source in sources.values()))
        self.assertTrue(self.sync(render=True))
        self.assertFalse((self.project / "examples").exists())
        self.assertFalse((self.project / "assets").exists())
        self.assertFalse((self.project / "node_modules").exists())
        requirements = (ROOT / "requirements-framework.txt").read_text().lower()
        self.assertNotIn("pillow", requirements)
        self.assertNotIn("playwright", requirements)

    def test_preserves_project_files_and_git_index(self):
        protected = {
            "setup.py": "raise RuntimeError('application setup must never run')\n",
            "requirements.txt": "application-package==1\n",
            "docs/ARCHITECTURE_GUARDRAILS.md": "Project-specific constraints\n",
            "docs/DEPLOY_CONTRACTS.md": "custom deployment\n",
            ".github/pull_request_template.md": "custom PR\n",
            ".github/workflows/agent-quality.yml": "custom CI\n",
            ".codex/config.toml": 'model = "custom-model"\n',
            "docs/TASKS.md": "project tasks\n",
        }
        for rel, content in protected.items():
            p = self.project / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        subprocess.run(["git", "-C", str(self.project), "add", "."], check=True)
        index_before = (self.project / ".git/index").read_bytes()
        self.assertTrue(self.sync(render=True))
        self.assertEqual((self.project / ".git/index").read_bytes(), index_before)
        for rel, content in protected.items():
            self.assertEqual((self.project / rel).read_text(), content, rel)

    def test_repeated_sync_is_noop_and_all_templates_render(self):
        self.assertTrue(self.sync(render=True))
        before = snapshot(self.project)
        with patch.object(sync, "atomic_write", side_effect=AssertionError("Unexpected write")):
            self.assertTrue(self.sync(render=True))
        self.assertEqual(snapshot(self.project), before)
        for rel in deployment_sources(ROOT):
            if sync.is_template(rel):
                self.assertFalse(setup.has_variables((self.project / rel).read_text()), str(rel))
        self.assertIn("Trial Project", (self.project / "agents/builder.md").read_text())

    def test_clone_without_ignored_cache_can_reconfigure(self):
        import shutil
        self.assertTrue(self.sync(render=True))
        clone = self.base / "clone"
        shutil.copytree(self.project, clone, ignore=shutil.ignore_patterns(".templates", ".agent"))
        (clone / "project.config.yaml").write_text('project: {name: "After Clone"}\n')
        result = self.command(clone / ".agent-system/setup.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("After Clone", (clone / "AGENTS.md").read_text())
        self.assertTrue((clone / ".agent-system/templates/AGENTS.md").exists())

    def test_seed_history_not_inherited_from_framework(self):
        self.assertTrue(self.sync(render=True))
        self.assertNotIn("TASK-001", (self.project / "docs/TASKS.md").read_text())
        self.assertNotIn("DEC-014", (self.project / "docs/DECISIONS.md").read_text())
        self.assertNotIn("Unfolda", (self.project / "docs/LESSONS_LEARNED.md").read_text())

    def test_invalid_config_has_no_partial_sync(self):
        for invalid in ["null\n", "project: []\n", 'project: {name: "x"}\nanalytics_by_default: "false"\n', "project: [bad\n"]:
            (self.project / "project.config.yaml").write_text(invalid)
            before = snapshot(self.project)
            self.assertFalse(self.sync(render=True))
            self.assertEqual(snapshot(self.project), before)

    def test_bad_template_has_no_partial_sync(self):
        broken = self.base / "broken.md"
        broken.write_text("{{ missing.required }}")
        before = snapshot(self.project)
        sources = deployment_sources(ROOT)
        sources[Path("agents/builder.md")] = broken
        with patch.object(sync, "deployment_sources", return_value=sources):
            self.assertFalse(self.sync(render=True))
        self.assertEqual(snapshot(self.project), before)

    def test_refuses_symlinked_destination(self):
        outside = self.base / "outside"
        outside.mkdir()
        (self.project / "agents").symlink_to(outside, target_is_directory=True)
        self.assertFalse(self.sync(render=True))
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.project / "AGENTS.md").exists())

    def test_refuses_self_sync(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertFalse(sync.cmd_sync(ROOT, render=True))

    def test_malformed_ignore_block_stops_before_copy(self):
        (self.project / ".gitignore").write_text(sync.GITIGNORE_MARKER_START + "\n")
        before = snapshot(self.project)
        self.assertFalse(self.sync(render=True))
        self.assertEqual(snapshot(self.project), before)

    def test_old_ignore_block_migrates_without_index_changes(self):
        (self.project / ".gitignore").write_text("custom/\n" + sync.GITIGNORE_MARKER_START + "\n/AGENTS.md\n/agents/\n" + sync.GITIGNORE_MARKER_END + "\nother/\n")
        self.assertTrue(self.sync(render=True))
        text = (self.project / ".gitignore").read_text()
        self.assertIn("custom/", text)
        self.assertIn("other/", text)
        self.assertNotIn("/AGENTS.md", text)
        self.assertNotIn("/agents/", text)

    def test_template_to_static_update_does_not_resurrect_old_policy(self):
        self.assertTrue(self.sync(render=True))
        source = self.base / "static.md"
        source.write_text("# Static replacement\n")
        sources = deployment_sources(ROOT)
        sources[Path("AGENTS.md")] = source
        with patch.object(sync, "deployment_sources", return_value=sources):
            self.assertTrue(self.sync(render=True))
        result = self.command(self.project / ".agent-system/setup.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.project / "AGENTS.md").read_text(), source.read_text())

    def test_reconfigure_preserves_project_owned_docs(self):
        self.assertTrue(self.sync(render=True))
        deployment = self.project / "docs/DEPLOY_CONTRACTS.md"
        deployment.write_text("User revised deployment {{ literal }}\n")
        (self.project / "project.config.yaml").write_text('project: {name: "Renamed"}\n')
        result = self.command(self.project / ".agent-system/setup.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Renamed", (self.project / "AGENTS.md").read_text())
        self.assertEqual(deployment.read_text(), "User revised deployment {{ literal }}\n")

    def test_legacy_pipeline_configuration_and_restore(self):
        (self.project / "project.config.yaml").write_bytes((ROOT / "examples/unfolda/project.config.yaml").read_bytes())
        self.assertTrue(self.sync(render=True))
        self.assertIn("ingestion → segmentation → translation → formatting → export", (self.project / "AGENTS.md").read_text())
        before = snapshot(self.project)
        self.assertEqual(self.command(self.project / ".agent-system/setup.py", "--restore").returncode, 0)
        self.assertEqual(self.command(self.project / ".agent-system/setup.py").returncode, 0)
        self.assertEqual(snapshot(self.project), before)

    def test_renderer_validates_all_before_writing(self):
        self.assertTrue(self.sync(render=True))
        (self.project / "agents/builder.md").write_text("{{ missing.value }}")
        before = snapshot(self.project)
        result = self.command(self.project / ".agent-system/setup.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(snapshot(self.project), before)

    def test_bootstrap_quotes_unicode_and_idempotence(self):
        name = 'Game "Астра": \\ $()'
        project = self.base / "O'Brien project"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(bootstrap.initialize(name, project, register=False))
            self.assertTrue(bootstrap.initialize(name, project, register=False))
        self.assertEqual(setup.load_config(project / "project.config.yaml")["project"]["name"], name)
        with self.assertRaises(ValueError):
            bootstrap.initialize("Different", project, register=False)

    def test_audit_without_registry_returns_json(self):
        result = self.command(ROOT / "audit.py", "--local", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["projects_audited"], [])
        self.assertTrue(any(f["category"] == "contracts" for f in data["findings"]))

    def test_audit_critical_findings_fail_cli(self):
        report = {"summary": {"critical": 1, "warnings": 0}, "findings": []}
        with patch.object(sys, "argv", ["audit.py", "--local", "--json"]), patch.object(audit, "run_audit", return_value=report), contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as exc:
            audit.main()
        self.assertEqual(exc.exception.code, 1)

    def test_audit_detects_static_and_rendered_content_drift(self):
        self.assertTrue(self.sync(render=True))
        self.assertFalse([f for f in audit.check_integrity([self.project]) if f["severity"] != "info"])
        for rel in ["AGENTS.md", "docs/CODING_RULES.md"]:
            (self.project / rel).write_text("locally modified\n")
        findings = audit.check_integrity([self.project])
        paths = [p for f in findings for p in f["files_affected"]]
        self.assertIn("AGENTS.md", paths)
        self.assertIn("docs/CODING_RULES.md", paths)

    def test_default_telemetry_never_scans_private_transcripts(self):
        with patch.object(metrics_workflow, "find_session_files", side_effect=AssertionError("Unrequested transcript access")):
            self.assertIsNone(metrics_workflow.collect()["cost_30d"]["total_cost_usd"])
            with patch.object(sys, "argv", ["metrics_workflow.py"]), contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(metrics_workflow.main(), 0)
            self.assertFalse(json.loads(out.getvalue())["available"])
        self.assertEqual(metrics.format_usd(None), "unknown")
        self.assertIn("unavailable", metrics._render_workflow_section(metrics_workflow.collect()))

    def test_hook_install_preserves_existing_hooks_before_any_write(self):
        hooks = self.base / "hooks"
        hooks.mkdir()
        custom = hooks / "post-commit"
        custom.write_text("custom user hook\n")
        with self.assertRaises(ValueError):
            hook_installer.install(hooks)
        self.assertEqual(custom.read_text(), "custom user hook\n")
        self.assertFalse((hooks / "pre-commit").exists())


if __name__ == "__main__":
    unittest.main()
