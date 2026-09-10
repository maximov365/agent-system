"""Failure recovery, migration identity, and cooperative concurrent-writer tests."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sync
import sync_transaction as tx


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.target = self.base / "project"
        self.target.mkdir()
        self.root = tx.backup_root(self.target)
        (self.target / "project.config.yaml").write_text('project: {name: "Recovery game"}\n')

    def apply(self, pending, **kwargs):
        with tx.project_lock(self.target, self.root):
            return tx.apply_batch(self.target, pending, root=self.root, **kwargs)

    def test_failure_restores_files_modes_and_version(self):
        existing = self.target / "AGENTS.md"
        existing.write_text("old")
        existing.chmod(0o640)
        (self.target / ".agent-system-version").write_text("old version")
        def fail(path, data):
            if path.name == ".agent-system-version":
                raise OSError("simulated disk failure")
            tx.atomic_write(path, data)
        with self.assertRaises(OSError), contextlib.redirect_stdout(io.StringIO()):
            self.apply({Path("AGENTS.md"): b"new", Path("new.txt"): b"new",
                        Path(".agent-system-version"): b"new version"}, writer=fail)
        self.assertEqual(existing.read_text(), "old")
        self.assertEqual(existing.stat().st_mode & 0o777, 0o640)
        self.assertFalse((self.target / "new.txt").exists())
        self.assertEqual((self.target / ".agent-system-version").read_text(), "old version")
        record = next(self.root.glob("*/manifest.json"))
        self.assertEqual(json.loads(record.read_text())["status"], "rolled_back")

    def test_restore_handles_created_deleted_and_replaced_files(self):
        (self.target / "kept").write_text("before")
        (self.target / "deleted").write_text("original")
        backup = self.apply({Path("kept"): b"after", Path("added"): b"new", Path("deleted"): None})
        pending, modes = tx.restore_plan(self.target, backup)
        reverse = self.apply(pending, modes=modes)
        self.assertEqual((self.target / "kept").read_text(), "before")
        self.assertEqual((self.target / "deleted").read_text(), "original")
        self.assertFalse((self.target / "added").exists())
        self.assertIsNotNone(reverse)

    def test_restore_rejects_new_edits_before_any_write(self):
        (self.target / "one").write_text("old")
        backup = self.apply({Path("one"): b"new", Path("two"): b"created"})
        (self.target / "two").write_text("user edit")
        with self.assertRaisesRegex(ValueError, "Newer local edit"):
            tx.restore_plan(self.target, backup)
        self.assertEqual((self.target / "one").read_text(), "new")

    def test_restore_rejects_corrupted_backup_and_wrong_target(self):
        (self.target / "one").write_text("old")
        backup = self.apply({Path("one"): b"new"})
        with self.assertRaisesRegex(ValueError, "another target"):
            tx.restore_plan(self.base, backup)
        (backup / "before/one").write_text("tampered")
        with self.assertRaisesRegex(ValueError, "Backup content changed"):
            tx.restore_plan(self.target, backup)

    def test_writer_lock_independent_of_backup_location(self):
        with tx.project_lock(self.target, self.root):
            with self.assertRaisesRegex(ValueError, "Another framework writer"):
                with tx.project_lock(self.target, self.base / "other-backups"):
                    self.fail("second writer entered")

    def test_backups_cannot_be_inside_target_or_through_symlink(self):
        with self.assertRaises(ValueError):
            tx.backup_root(self.target, self.target / "backups")
        (self.base / "link").symlink_to(self.target)
        with self.assertRaises(ValueError):
            tx.backup_root(self.target, self.base / "link/backups")
        with self.assertRaises(ValueError):
            self.apply({Path(".git/config"): b"danger"})

    def test_exact_legacy_migration_and_no_write_preview(self):
        legacy = Path(__file__).parent / "fixtures/legacy-setup-v1.0.40.txt"
        (self.target / "setup.py").write_bytes(legacy.read_bytes())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(sync.cmd_sync(self.target, render=True, dry_run=True))
        self.assertFalse(self.root.exists())
        self.assertEqual((self.target / "setup.py").read_bytes(), legacy.read_bytes())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(sync.cmd_sync(self.target, render=True))
        self.assertIn('runpy.run_path', (self.target / "setup.py").read_text())
        self.assertIn('.agent-system', (self.target / "setup.py").read_text())
        backup = next(self.root.glob("*/manifest.json")).parent
        self.assertEqual((backup / "before/setup.py").read_bytes(), legacy.read_bytes())

    def test_similar_but_custom_legacy_file_is_preserved(self):
        legacy = Path(__file__).parent / "fixtures/legacy-setup-v1.0.40.txt"
        custom = legacy.read_bytes() + b"\n# project modification\n"
        (self.target / "setup.py").write_bytes(custom)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(sync.cmd_sync(self.target, render=True))
        self.assertEqual((self.target / "setup.py").read_bytes(), custom)

    def test_restore_preview_does_not_create_another_backup(self):
        backup = self.apply({Path("one"): b"new"})
        before = set(self.root.iterdir())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(sync.cmd_restore(self.target, backup, dry_run=True))
        self.assertEqual(set(self.root.iterdir()), before)
        self.assertEqual((self.target / "one").read_bytes(), b"new")

    def test_rollback_does_not_overwrite_a_concurrent_edit(self):
        (self.target / "one").write_text("old")
        def conflict(path, data):
            tx.atomic_write(path, b"user edit")
            raise OSError("writer interrupted by a concurrent edit")
        with self.assertRaises(OSError), contextlib.redirect_stdout(io.StringIO()):
            self.apply({Path("one"): b"new"}, writer=conflict)
        self.assertEqual((self.target / "one").read_text(), "user edit")
        record = json.loads(next(self.root.glob("*/manifest.json")).read_text())
        self.assertEqual(record["status"], "recovery_required")


if __name__ == "__main__":
    unittest.main()
