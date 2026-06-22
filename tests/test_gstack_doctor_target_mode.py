import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_PROJECT = REPO_ROOT / "scripts" / "init_project.py"


class GStackDoctorTargetModeTest(unittest.TestCase):
    def test_installed_target_repo_does_not_require_source_distribution_docs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            target = tmp / "doctor-target"
            target.mkdir()

            install = subprocess.run(
                [
                    sys.executable,
                    str(INIT_PROJECT),
                    "--repo-root",
                    str(target),
                    "--project-name",
                    "Doctor Target",
                    "--adapter",
                    "default",
                    "--apply-runtime",
                    "--rewrite-adapter",
                    "--formal-stack-prefix",
                    "stack/doctor-target/",
                    "--domain-spec-prefix",
                    "stack/doctor-target/specs/",
                    "--implementation-prefix",
                    "stack/doctor-target/src/",
                    "--report",
                ],
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            boundary_dir = target / ".gstack" / "task-boundaries"
            boundary = boundary_dir / "doctor-target.md"
            boundary.write_text(
                "# Doctor Target Boundary\n\n"
                "## Goal\n\n"
                "Verify target-aware doctor behavior.\n",
                encoding="utf-8",
            )
            (boundary_dir / "CURRENT.local.md").write_text(
                "# 当前本地 Active Boundary\n\n"
                "## Active Boundary\n\n"
                "- [doctor-target.md](doctor-target.md)\n",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["CODEX_HOME"] = str(tmp / "codex-home")
            env.pop("KK_ACTIVE_BOUNDARY", None)
            env.pop("KK_ADAPTER", None)
            env.pop("KK_ADAPTER_RUNTIME", None)

            result = subprocess.run(
                [
                    sys.executable,
                    ".gstack/scripts/gstack_doctor.py",
                    "check",
                ],
                cwd=target,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )

            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("检查模式: target-repo", output)
            self.assertIn("source-only 发布资料不要求", output)
            self.assertNotIn("QUICK_START_FOR_PARTNERS.md", output)
            self.assertNotIn("plugins/MARKETPLACE_INSTALL.md", output)


if __name__ == "__main__":
    unittest.main()
