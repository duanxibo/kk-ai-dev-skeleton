import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "init_project.py"


def load_module():
    spec = importlib.util.spec_from_file_location("init_project", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["init_project"] = module
    spec.loader.exec_module(module)
    return module


class InitProjectTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.module = load_module()
        self.module.REPO_ROOT = self.root
        self.module.DEFAULT_ADAPTER = self.root / "adapters" / "default"
        self.module.ACTIVE_BOUNDARY = (
            self.root / ".gstack" / "task-boundaries" / "CURRENT.local.md"
        )

        default_adapter = self.module.DEFAULT_ADAPTER
        default_adapter.mkdir(parents=True)
        (default_adapter / "adapter.md").write_text("# Default Adapter\n", encoding="utf-8")
        (default_adapter / "runtime.json").write_text(
            '{"version": 1, "name": "default"}\n',
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_slugify_normalizes_adapter_name(self):
        self.assertEqual(self.module.slugify(" My_Project 01 "), "my-project-01")
        self.assertEqual(self.module.slugify("中文项目"), "project")

    def test_apply_adapter_creates_from_default(self):
        result = self.module.apply_adapter("demo", force=False)

        self.assertTrue(result.created)
        self.assertFalse(result.replaced)
        self.assertTrue((self.root / "adapters" / "demo" / "adapter.md").exists())
        runtime_text = (self.root / "adapters" / "demo" / "runtime.json").read_text(
            encoding="utf-8"
        )
        self.assertIn('"name": "demo"', runtime_text)

    def test_apply_adapter_does_not_overwrite_without_force(self):
        adapter_dir = self.root / "adapters" / "demo"
        adapter_dir.mkdir(parents=True)
        marker = adapter_dir / "adapter.md"
        marker.write_text("keep me\n", encoding="utf-8")
        (adapter_dir / "runtime.json").write_text('{"name": "demo"}\n', encoding="utf-8")

        result = self.module.apply_adapter("demo", force=False)

        self.assertFalse(result.created)
        self.assertFalse(result.replaced)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep me\n")

    def test_detect_project_reports_adapter_and_missing_core(self):
        self.module.apply_adapter("demo", force=False)

        state = self.module.detect_project("demo")

        self.assertTrue(state["adapter_exists"])
        self.assertTrue(state["adapter_md_exists"])
        self.assertTrue(state["runtime_json_exists"])
        self.assertIn("AGENTS.md", state["core_missing"])

    def test_plan_adoption_preserves_existing_adapter(self):
        self.module.apply_adapter("demo", force=False)
        state = self.module.detect_project("demo")

        plan = self.module.plan_adoption(state)

        self.assertTrue(any("保留现有 adapters/demo" in step for step in plan))
        self.assertTrue(any("自然语言" in step for step in plan))

    def test_verify_commands_uses_active_boundary_when_present(self):
        boundary_dir = self.root / ".gstack" / "task-boundaries"
        boundary_dir.mkdir(parents=True)
        self.module.ACTIVE_BOUNDARY.write_text(
            "- [demo-boundary.md](demo-boundary.md)\n",
            encoding="utf-8",
        )

        commands = dict(self.module.verify_commands())

        self.assertIn("--boundary", commands["required-gates"])
        self.assertIn(
            ".gstack/task-boundaries/demo-boundary.md",
            commands["required-gates"],
        )

    def test_report_includes_low_risk_pilot(self):
        state = self.module.detect_project("demo")

        report = self.module.render_report("demo", state)

        self.assertIn("KK Dev Skeleton 接入报告", report)
        self.assertIn("第一个低风险试点任务", report)


if __name__ == "__main__":
    unittest.main()
