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
            '{"version": 1, "name": "default", "paths": {"implementation_prefixes": ["stack/default/src/"]}}\n',
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_slugify_normalizes_adapter_name(self):
        self.assertEqual(self.module.slugify(" My_Project 01 "), "my-project-01")
        self.assertEqual(self.module.slugify("中文项目"), "project")

    def test_apply_adapter_creates_from_default(self):
        (self.module.DEFAULT_ADAPTER / "runtime.json").write_text(
            '{"version": 1, "name": "default", "paths": {"implementation_prefixes": ["stack/default/src/"]}}\n',
            encoding="utf-8",
        )

        result = self.module.apply_adapter("demo", force=False)

        self.assertTrue(result.created)
        self.assertFalse(result.replaced)
        self.assertTrue(result.stack_created)
        self.assertTrue((self.root / "adapters" / "demo" / "adapter.md").exists())
        self.assertTrue((self.root / "stack" / "demo" / "README.md").exists())
        self.assertTrue((self.root / "stack" / "demo" / "specs" / "README.md").exists())
        self.assertTrue((self.root / "stack" / "demo" / "src" / ".gitkeep").exists())
        self.assertTrue((self.root / "stack" / "demo" / "tests" / ".gitkeep").exists())
        self.assertTrue((self.root / "stack" / "demo" / "fixtures" / ".gitkeep").exists())
        self.assertTrue((self.root / "stack" / "demo" / "scripts" / ".gitkeep").exists())
        self.assertTrue((self.root / "archive" / "README.md").exists())
        self.assertTrue((self.root / "archive" / "baseline" / "README.md").exists())
        self.assertTrue((self.root / "blueprint" / "README.md").exists())
        self.assertTrue((self.root / "blueprint" / "00_阅读入口.md").exists())
        self.assertTrue((self.root / "shared" / "README.md").exists())
        self.assertTrue((self.root / "shared" / "raw-inputs" / ".gitkeep").exists())
        self.assertTrue((self.root / ".gstack" / "designs" / "README.md").exists())
        self.assertTrue((self.root / ".gstack" / "migrations" / "README.md").exists())
        runtime_text = (self.root / "adapters" / "demo" / "runtime.json").read_text(
            encoding="utf-8"
        )
        self.assertIn('"name": "demo"', runtime_text)
        self.assertIn('"stack/demo/src/"', runtime_text)
        self.assertNotIn("stack/default/src/", runtime_text)

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
        self.assertTrue((self.root / "stack" / "demo" / "README.md").exists())

    def test_detect_project_reports_adapter_and_missing_core(self):
        self.module.apply_adapter("demo", force=False)

        state = self.module.detect_project("demo")

        self.assertTrue(state["adapter_exists"])
        self.assertTrue(state["adapter_md_exists"])
        self.assertTrue(state["runtime_json_exists"])
        self.assertTrue(state["stack_dir_exists"])
        self.assertTrue(state["stack_specs_exists"])
        self.assertTrue(state["stack_src_exists"])
        self.assertIn("AGENTS.md", state["core_missing"])
        self.assertTrue(state["runtime_stack_aligned"])
        self.assertTrue(state["workspace_layers"]["archive"])
        self.assertTrue(state["workspace_layers"]["archive_baseline"])
        self.assertTrue(state["workspace_layers"]["blueprint"])
        self.assertTrue(state["workspace_layers"]["shared"])
        self.assertTrue(state["workspace_layers"]["gstack_designs"])
        self.assertTrue(state["workspace_layers"]["gstack_migrations"])

    def test_detect_project_reports_root_code_migration_candidates(self):
        (self.root / "src").mkdir()
        (self.root / "prisma").mkdir()
        (self.root / "package.json").write_text('{"scripts": {}}\n', encoding="utf-8")

        state = self.module.detect_project("demo")

        self.assertIn("src", state["root_code_paths"])
        self.assertIn("prisma", state["root_code_paths"])
        self.assertIn("package.json", state["root_code_paths"])

    def test_plan_adoption_preserves_existing_adapter(self):
        self.module.apply_adapter("demo", force=False)
        state = self.module.detect_project("demo")

        plan = self.module.plan_adoption(state)

        self.assertTrue(any("保留现有 adapters/demo" in step for step in plan))
        self.assertTrue(any("stack/demo" in step for step in plan))
        self.assertTrue(any("workspace layers" in step for step in plan))
        self.assertTrue(any("自然语言" in step for step in plan))

    def test_plan_adoption_mentions_root_code_migration(self):
        (self.root / "src").mkdir()
        state = self.module.detect_project("demo")

        plan = self.module.plan_adoption(state)

        self.assertTrue(any("迁移计划" in step for step in plan))

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
        self.assertIn("stack dir", report)
        self.assertIn("workspace layers", report)
        self.assertIn("第一个低风险试点任务", report)

    def test_workspace_layers_preserve_existing_readme(self):
        archive_readme = self.root / "archive" / "README.md"
        archive_readme.parent.mkdir(parents=True)
        archive_readme.write_text("custom archive rules\n", encoding="utf-8")

        created = self.module.ensure_workspace_layers()

        self.assertEqual(archive_readme.read_text(encoding="utf-8"), "custom archive rules\n")
        self.assertNotIn("archive/README.md", created)
        self.assertTrue((self.root / "blueprint" / "README.md").exists())
        self.assertTrue((self.root / "shared" / "generated" / ".gitkeep").exists())

    def test_upgrade_plan_for_existing_project_does_not_reinitialize(self):
        self.module.apply_adapter("demo", force=False)
        (self.root / "src").mkdir()
        state = self.module.detect_project("demo")

        plan = self.module.plan_project_upgrade("demo", state)
        rendered = self.module.render_upgrade_plan("demo", state)

        self.assertTrue(any(item["id"] == "project-adapter" for item in plan))
        adapter_item = next(item for item in plan if item["id"] == "project-adapter")
        self.assertEqual(adapter_item["status"], "done")
        self.assertIn("不新建项目、不重新接入", rendered)
        self.assertIn("root-code-migration", rendered)
        self.assertIn("src", rendered)

    def test_upgrade_plan_marks_stack_layout_safe_when_missing(self):
        adapter_dir = self.root / "adapters" / "demo"
        adapter_dir.mkdir(parents=True)
        (adapter_dir / "adapter.md").write_text("keep me\n", encoding="utf-8")
        (adapter_dir / "runtime.json").write_text(
            '{"name": "demo", "paths": {"implementation_prefixes": ["src/"]}}\n',
            encoding="utf-8",
        )

        state = self.module.detect_project("demo")
        plan = self.module.plan_project_upgrade("demo", state)
        stack_item = next(item for item in plan if item["id"] == "stack-layout")
        runtime_item = next(
            item for item in plan if item["id"] == "adapter-runtime-stack-routing"
        )

        self.assertEqual(stack_item["status"], "planned")
        self.assertTrue(stack_item["safe_apply"])
        self.assertIn("--upgrade-apply", stack_item["command"])
        self.assertEqual(runtime_item["status"], "planned")
        self.assertFalse(runtime_item["safe_apply"])

    def test_upgrade_apply_preserves_adapter_and_creates_stack(self):
        adapter_dir = self.root / "adapters" / "demo"
        adapter_dir.mkdir(parents=True)
        adapter_md = adapter_dir / "adapter.md"
        adapter_md.write_text("custom adapter\n", encoding="utf-8")
        (adapter_dir / "runtime.json").write_text('{"name": "demo"}\n', encoding="utf-8")
        (self.root / "src").mkdir()

        result = self.module.apply_project_upgrade("demo")

        self.assertTrue(result.applied)
        self.assertFalse(result.blocked)
        self.assertTrue(result.stack_created)
        self.assertEqual(adapter_md.read_text(encoding="utf-8"), "custom adapter\n")
        self.assertTrue((self.root / "stack" / "demo" / "README.md").exists())
        self.assertIn("src", result.root_code_paths)

    def test_upgrade_apply_blocks_when_adapter_missing(self):
        result = self.module.apply_project_upgrade("demo")

        self.assertFalse(result.applied)
        self.assertTrue(result.blocked)
        self.assertIn("首次接入", result.message)


if __name__ == "__main__":
    unittest.main()
