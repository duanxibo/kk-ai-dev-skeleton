import importlib.util
import os
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
                module.REPO_ROOT = tmp / "tiangong" / "ai-dev-skeleton"

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

    def test_local_setup_script_has_valid_bash_syntax(self):
        result = subprocess.run(
            ["bash", "-n", str(SETUP_SCRIPT)],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_partner_quick_start_is_linked_from_readme(self):
        readme_text = README.read_text(encoding="utf-8")
        quick_start_text = PARTNER_QUICK_START.read_text(encoding="utf-8")

        self.assertIn("QUICK_START_FOR_PARTNERS.md", readme_text)
        self.assertIn("请使用 KK Dev Skeleton Adoption", quick_start_text)
        self.assertIn("不要连接真实数据、生产环境、数据库", quick_start_text)


if __name__ == "__main__":
    unittest.main()
