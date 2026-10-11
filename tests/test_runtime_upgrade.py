"""Transactional upgrades preserve old runtime on actual failure scenarios."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".gstack/scripts"))
import runtime_upgrade


class RuntimeUpgradeTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.source, self.target = self.root / "source", self.root / "target"
        self.files = [".gstack/scripts/a.py", ".gstack/scripts/b.py"]
        hashes = {}
        for relative in self.files:
            for root, data in ((self.source, b"VALUE = 2\n"), (self.target, b"VALUE = 1\n")):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            hashes[relative] = hashlib.sha256(b"VALUE = 1\n").hexdigest()
        (self.target / runtime_upgrade.MANIFEST).write_text(json.dumps(dict(release_version="old", files=hashes)))

    def snapshot(self):
        return {str(path.relative_to(self.target)): (path.read_bytes(), path.stat().st_mode)
                for path in self.target.rglob("*") if path.is_file()}

    def upgrade(self, **kwargs):
        return runtime_upgrade.upgrade_runtime_bundle(source_root=self.source, target_root=self.target,
                                                     files=self.files, dry_run=False,
                                                     release_version="new", **kwargs)

    def test_pristine_upgrade_checks_entire_stage_and_commits_manifest(self):
        def check(stage):
            for relative in self.files:
                self.assertEqual((stage / relative).read_text(), "VALUE = 2\n")
        result = self.upgrade(compatibility_check=check)
        self.assertTrue(result["ok"])
        self.assertEqual(result["updated_paths"], self.files)
        self.assertEqual(json.loads((self.target / runtime_upgrade.MANIFEST).read_text())["release_version"], "new")

    def test_conflict_blocks_pristine_file_and_manifest_too(self):
        (self.target / self.files[1]).write_text("CUSTOM = True\n")
        before = self.snapshot()
        result = self.upgrade()
        self.assertEqual(result["upgrade_status"], "conflicts-preserved")
        self.assertEqual(before, self.snapshot())

    def test_missing_source_blocks_every_write(self):
        (self.source / self.files[1]).unlink()
        before = self.snapshot()
        self.assertEqual(self.upgrade()["upgrade_status"], "missing-source")
        self.assertEqual(before, self.snapshot())

    def test_syntax_error_blocks_before_write(self):
        (self.source / self.files[1]).write_text("def invalid(\n")
        before = self.snapshot()
        self.assertEqual(self.upgrade()["upgrade_status"], "verification-failed")
        self.assertEqual(before, self.snapshot())

    def test_target_compatibility_failure_preserves_all(self):
        before = self.snapshot()
        self.assertEqual(self.upgrade(compatibility_check=lambda stage: False)["upgrade_status"], "verification-failed")
        self.assertEqual(before, self.snapshot())

    def test_missing_cli_dependency_blocks_upgrade(self):
        relative = ".gstack/scripts/gstack_loop.py"
        self.files.append(relative)
        (self.source / relative).write_text("import missing_upgrade_dependency\n")
        before = self.snapshot()
        self.assertEqual(self.upgrade()["upgrade_status"], "verification-failed")
        self.assertEqual(before, self.snapshot())

    def test_existing_invalid_manifest_cannot_be_replaced(self):
        (self.target / runtime_upgrade.MANIFEST).write_text("{}")
        before = self.snapshot()
        self.assertEqual(self.upgrade()["upgrade_status"], "blocked")
        self.assertEqual(before, self.snapshot())

    def test_manifest_write_failure_restores_new_and_overwritten_files(self):
        (self.target / self.files[1]).unlink()
        before = self.snapshot()
        original = runtime_upgrade._write
        def failing(path, data, mode):
            if path == self.target / runtime_upgrade.MANIFEST:
                raise OSError("injected manifest failure")
            original(path, data, mode)
        with patch.object(runtime_upgrade, "_write", side_effect=failing):
            result = self.upgrade()
        self.assertEqual(result["upgrade_status"], "rolled-back")
        self.assertEqual(before, self.snapshot())

    def test_dry_run_runs_verification_without_writes(self):
        before = self.snapshot()
        result = runtime_upgrade.upgrade_runtime_bundle(source_root=self.source, target_root=self.target,
                                                       files=self.files, dry_run=True, release_version="new")
        self.assertTrue(result["ok"])
        self.assertFalse(result["upgrade_complete"])
        self.assertEqual(result["would_create"], self.files)
        self.assertEqual(before, self.snapshot())

    def test_no_baseline_differences_are_not_overwritten(self):
        (self.target / runtime_upgrade.MANIFEST).unlink()
        before = self.snapshot()
        self.assertEqual(self.upgrade()["upgrade_status"], "conflicts-preserved")
        self.assertEqual(before, self.snapshot())

    def test_symlink_target_is_rejected_without_external_write(self):
        path = self.target / self.files[1]
        path.unlink()
        external = self.root / "external"
        external.write_text("KEEP\n")
        path.symlink_to(external)
        self.assertEqual(self.upgrade()["upgrade_status"], "blocked")
        self.assertEqual(external.read_text(), "KEEP\n")

    def test_cooperating_upgrade_lock_blocks_writes(self):
        (self.target / runtime_upgrade.LOCK).write_text("busy")
        before = self.snapshot()
        self.assertEqual(self.upgrade()["upgrade_status"], "locked")
        self.assertEqual(before, self.snapshot())

    def test_intervening_edit_is_preserved(self):
        def modify(stage):
            (self.target / self.files[0]).write_text("USER_EDIT = 1\n")
        result = self.upgrade(compatibility_check=modify)
        self.assertEqual(result["upgrade_status"], "conflicts-preserved")
        self.assertEqual((self.target / self.files[0]).read_text(), "USER_EDIT = 1\n")
        self.assertEqual((self.target / self.files[1]).read_text(), "VALUE = 1\n")


if __name__ == "__main__":
    unittest.main()
