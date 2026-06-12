import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPO_ROOT
    / "plugins"
    / "kk-dev-skeleton-adoption"
    / "scripts"
    / "check_update.py"
)


def write_manifest(plugin_root: Path, version: str) -> Path:
    manifest_dir = plugin_root / ".codex-plugin"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "plugin.json"
    manifest_path.write_text(
        json.dumps(
            {
                "name": "kk-dev-skeleton-adoption",
                "version": version,
            }
        ),
        encoding="utf-8",
    )
    return manifest_path


class PluginUpdateCheckTest(unittest.TestCase):
    def run_checker(self, plugin_root: Path, remote_path: Path, *extra: str):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--plugin-root",
                str(plugin_root),
                "--remote-url",
                str(remote_path),
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_reports_current_when_versions_match(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "plugin"
            remote = Path(tmpdir) / "latest.json"
            write_manifest(root, "0.1.0+codex.1")
            remote.write_text(
                json.dumps({"version": "0.1.0+codex.1"}),
                encoding="utf-8",
            )

            result = self.run_checker(root, remote, "--format", "json")

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "current")
        self.assertEqual(payload["local_version"], "0.1.0+codex.1")
        self.assertEqual(payload["latest_version"], "0.1.0+codex.1")

    def test_reports_outdated_with_upgrade_instruction(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "plugin"
            remote = Path(tmpdir) / "latest.json"
            write_manifest(root, "0.1.0+codex.1")
            remote.write_text(
                json.dumps({"version": "0.1.0+codex.2"}),
                encoding="utf-8",
            )

            result = self.run_checker(root, remote)

        self.assertEqual(result.returncode, 0)
        self.assertIn("检测到 KK Dev Skeleton 插件有更新", result.stdout)
        self.assertIn("0.1.0+codex.1", result.stdout)
        self.assertIn("0.1.0+codex.2", result.stdout)
        self.assertIn(
            "codex plugin marketplace upgrade kk-dev-skeleton-internal",
            result.stdout,
        )

    def test_unknown_status_is_non_blocking_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "plugin"
            missing_remote = Path(tmpdir) / "missing.json"
            write_manifest(root, "0.1.0+codex.1")

            result = self.run_checker(root, missing_remote, "--format", "json")

        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "unknown")
        self.assertIn("FileNotFoundError", payload["error"])

    def test_reports_ahead_without_upgrade_instruction(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "plugin"
            remote = Path(tmpdir) / "latest.json"
            write_manifest(root, "0.1.0+codex.3")
            remote.write_text(
                json.dumps({"version": "0.1.0+codex.2"}),
                encoding="utf-8",
            )

            result = self.run_checker(root, remote)

        self.assertEqual(result.returncode, 0)
        self.assertIn("版本高于 GitHub main", result.stdout)
        self.assertNotIn("codex plugin marketplace upgrade", result.stdout)

    def test_strict_mode_exits_nonzero_when_outdated(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "plugin"
            remote = Path(tmpdir) / "latest.json"
            write_manifest(root, "0.1.0+codex.1")
            remote.write_text(
                json.dumps({"version": "0.1.0+codex.2"}),
                encoding="utf-8",
            )

            result = self.run_checker(root, remote, "--strict")

        self.assertEqual(result.returncode, 20)


if __name__ == "__main__":
    unittest.main()
