import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCTOR_PATH = REPO_ROOT / ".gstack" / "scripts" / "gstack_doctor.py"
DOCTOR_SCRIPT_DIR = DOCTOR_PATH.parent
SETUP_SCRIPT = REPO_ROOT / "scripts" / "setup_local_codex.sh"
PARTNER_QUICK_START = REPO_ROOT / "QUICK_START_FOR_PARTNERS.md"
README = REPO_ROOT / "README.md"
ADMIN_INSTALL_CHECKLIST = REPO_ROOT / "plugins" / "ADMIN_INSTALL_CHECKLIST.md"
MARKETPLACE_INSTALL = REPO_ROOT / "plugins" / "MARKETPLACE_INSTALL.md"


def tracked_files():
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return [
        REPO_ROOT / raw.decode("utf-8")
        for raw in result.stdout.split(b"\0")
        if raw
    ]


def load_doctor_module():
    if str(DOCTOR_SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(DOCTOR_SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("gstack_doctor", DOCTOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["gstack_doctor"] = module
    spec.loader.exec_module(module)
    return module


class ProductizationHardeningTest(unittest.TestCase):
    def test_parent_path_hint_does_not_make_context_isolation_warn(self):
        module = load_doctor_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            previous_codex_home = os.environ.get("CODEX_HOME")
            try:
                os.environ["CODEX_HOME"] = str(tmp / "codex-home")
                (tmp / "codex-home" / "skills").mkdir(parents=True)
                module.REPO_ROOT = tmp / ("tian" + "gong") / "ai-dev-skeleton"

                result = module.check_context_isolation()
            finally:
                if previous_codex_home is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = previous_codex_home

        self.assertEqual(result.status, "ok")
        self.assertIn("父目录命名提示", "\n".join(result.details))

    def test_external_skill_symlink_still_warns(self):
        module = load_doctor_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            previous_codex_home = os.environ.get("CODEX_HOME")
            try:
                skills = tmp / "codex-home" / "skills"
                skills.mkdir(parents=True)
                external = tmp / "other-project" / "tg-task-kickoff"
                external.parent.mkdir(parents=True)
                external.mkdir()
                (skills / "tg-task-kickoff").symlink_to(
                    external,
                    target_is_directory=True,
                )
                os.environ["CODEX_HOME"] = str(tmp / "codex-home")
                module.REPO_ROOT = tmp / "plain-parent" / "ai-dev-skeleton"

                result = module.check_context_isolation()
            finally:
                if previous_codex_home is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = previous_codex_home

        self.assertEqual(result.status, "warn")
        self.assertIn("外部项目 skill symlink", "\n".join(result.details))

    def test_context_isolation_next_step_distinguishes_nonlink_dirs(self):
        module = load_doctor_module()

        nonlink = module.CheckResult(
            "context-isolation",
            "warn",
            "检测到可能导致串味的外部上下文线索。",
            ["检测到外部项目 skill 普通目录；doctor 不会自动处理。"],
        )
        symlink = module.CheckResult(
            "context-isolation",
            "warn",
            "检测到可能导致串味的外部上下文线索。",
            ["外部 skill symlink:", "  - tg-task-kickoff -> /tmp/old"],
        )

        self.assertIn("普通目录", module.human_next_step(nonlink))
        self.assertIn("人工处理", module.human_next_step(nonlink))
        self.assertNotIn("清理外部 skill symlink", module.human_next_step(nonlink))
        self.assertIn("清理外部 skill symlink", module.human_next_step(symlink))

    def test_core_docs_cover_productization_entrypoints(self):
        module = load_doctor_module()
        required = set(module.REQUIRED_CORE_DOCS)

        expected = {
            "QUICK_START_FOR_PARTNERS.md",
            "COMPANY_ADOPTION_GUIDE.md",
            "CODEX_ADOPTION_CONNECTOR.md",
            "plugins/PARTNER_INSTALL.md",
            "plugins/MARKETPLACE_INSTALL.md",
            "plugins/ADMIN_INSTALL_CHECKLIST.md",
            "plugins/MARKETPLACE_ROLLOUT.md",
            "plugins/PILOT_FEEDBACK.md",
            ".agents/plugins/README.md",
            ".agents/plugins/marketplace.json",
            "scripts/setup_local_codex.sh",
            "blueprint/README.md",
            "archive/README.md",
            "archive/baseline/README.md",
            "shared/README.md",
        }

        self.assertTrue(expected.issubset(required))
        for entry in expected:
            self.assertTrue((REPO_ROOT / entry).exists(), entry)

    def test_local_setup_script_has_valid_bash_syntax(self):
        result = subprocess.run(
            ["bash", "-n", str(SETUP_SCRIPT)],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_local_setup_script_default_path_has_no_empty_array_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "skeleton"
            scripts_dir = root / "scripts"
            helper_dir = root / ".gstack" / "scripts"
            scripts_dir.mkdir(parents=True)
            helper_dir.mkdir(parents=True)
            setup_copy = scripts_dir / "setup_local_codex.sh"
            shutil.copy2(SETUP_SCRIPT, setup_copy)
            sync_stub = helper_dir / "sync_repo_skills.sh"
            sync_stub.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "echo sync-stub \"$@\"\n",
                encoding="utf-8",
            )
            sync_stub.chmod(0o755)
            doctor_stub = helper_dir / "gstack_doctor.py"
            doctor_stub.write_text(
                "print('doctor-stub')\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["bash", str(setup_copy)],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("sync-stub", result.stdout)
        self.assertIn("[SKIP] git hooks installation (not a git worktree)", result.stdout)
        self.assertIn("doctor-stub", result.stdout)

    def test_local_setup_script_skips_hooks_outside_git_worktree(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "skeleton"
            scripts_dir = root / "scripts"
            doctor_dir = root / ".gstack" / "scripts"
            scripts_dir.mkdir(parents=True)
            doctor_dir.mkdir(parents=True)
            setup_copy = scripts_dir / "setup_local_codex.sh"
            shutil.copy2(SETUP_SCRIPT, setup_copy)
            doctor_stub = doctor_dir / "gstack_doctor.py"
            doctor_stub.write_text(
                "print('doctor-stub')\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["bash", str(setup_copy), "--skip-skills"],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[SKIP] git hooks installation (not a git worktree)", result.stdout)
        self.assertIn("doctor-stub", result.stdout)

    def test_partner_quick_start_is_linked_from_readme(self):
        readme_text = README.read_text(encoding="utf-8")
        quick_start_text = PARTNER_QUICK_START.read_text(encoding="utf-8")

        self.assertIn("QUICK_START_FOR_PARTNERS.md", readme_text)
        self.assertIn("请使用 KK Dev Skeleton Adoption", quick_start_text)
        self.assertIn("不要连接真实数据、生产环境、数据库", quick_start_text)

    def test_public_plugin_install_docs_do_not_include_machine_paths(self):
        for path in (ADMIN_INSTALL_CHECKLIST, MARKETPLACE_INSTALL):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("/Users/" + "edy", text)
            self.assertNotIn(".codex/skills/.system", text)

    def test_tracked_public_distribution_has_no_local_or_legacy_names(self):
        forbidden = [
            "/Users/" + "edy",
            "task-" + "manager-cp",
            "Tian" + "Gong",
            "tian" + "gong",
        ]
        offenders = []
        for path in tracked_files():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in forbidden:
                if token in text:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}: {token}")

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
