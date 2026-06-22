import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "init_project.py"


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
        self.module.configure_repo_root(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def read_runtime(self, adapter="demo"):
        return json.loads(
            (self.root / "adapters" / adapter / "runtime.json").read_text(
                encoding="utf-8"
            )
        )

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), "--repo-root", str(self.root), *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_slugify_normalizes_adapter_name(self):
        self.assertEqual(self.module.slugify(" My_Project 01 "), "my-project-01")
        self.assertEqual(self.module.slugify("中文项目"), "default")

    def test_apply_creates_adapter_metadata_without_stack_layout(self):
        result = self.module.copy_default_adapter(
            "demo",
            force=False,
            dry_run=False,
            project_name="Demo Project",
        )

        self.assertTrue(result["created"])
        self.assertFalse(result["replaced"])
        self.assertTrue((self.root / "adapters" / "demo" / "adapter.md").exists())
        self.assertTrue((self.root / "adapters" / "demo" / "runtime.json").exists())
        self.assertFalse((self.root / "stack" / "demo").exists())

        runtime = self.read_runtime()
        self.assertEqual(runtime["version"], 7)
        self.assertEqual(runtime["name"], "demo")
        self.assertIn("online_flow_protocol", runtime)
        self.assertEqual(runtime["online_flow_protocol"]["status"], "supported")
        self.assertEqual(runtime["paths"]["implementation_prefixes"], [])

    def test_apply_preserves_existing_adapter_without_force(self):
        adapter_dir = self.root / "adapters" / "demo"
        adapter_dir.mkdir(parents=True)
        adapter_md = adapter_dir / "adapter.md"
        runtime_json = adapter_dir / "runtime.json"
        adapter_md.write_text("custom adapter\n", encoding="utf-8")
        runtime_json.write_text('{"name": "demo"}\n', encoding="utf-8")

        result = self.module.copy_default_adapter(
            "demo",
            force=False,
            dry_run=False,
            project_name="Demo Project",
        )

        self.assertFalse(result["created"])
        self.assertFalse(result["replaced"])
        self.assertIn("adapters/demo/adapter.md", result["preserved_paths"])
        self.assertEqual(adapter_md.read_text(encoding="utf-8"), "custom adapter\n")
        self.assertEqual(runtime_json.read_text(encoding="utf-8"), '{"name": "demo"}\n')

    def test_apply_force_replaces_non_default_adapter(self):
        adapter_dir = self.root / "adapters" / "demo"
        adapter_dir.mkdir(parents=True)
        adapter_md = adapter_dir / "adapter.md"
        adapter_md.write_text("custom adapter\n", encoding="utf-8")
        (adapter_dir / "runtime.json").write_text('{"name": "demo"}\n', encoding="utf-8")

        result = self.module.copy_default_adapter(
            "demo",
            force=True,
            dry_run=False,
            project_name="Demo Project",
        )

        self.assertTrue(result["replaced"])
        self.assertIn("Demo Project Adapter", adapter_md.read_text(encoding="utf-8"))
        self.assertEqual(self.read_runtime()["name"], "demo")

    def test_detect_project_reports_adapter_and_root_code_candidates(self):
        (self.root / "src").mkdir()
        (self.root / "prisma").mkdir()
        (self.root / "package.json").write_text('{"scripts": {}}\n', encoding="utf-8")
        self.module.copy_default_adapter(
            "demo",
            force=False,
            dry_run=False,
            project_name="Demo Project",
        )

        state = self.module.detect_project("demo")

        self.assertTrue(state["adapter_exists"])
        self.assertTrue(state["adapter_md_exists"])
        self.assertTrue(state["runtime_json_exists"])
        self.assertTrue(state["runtime_json_valid"])
        self.assertFalse(state["git_worktree"])
        self.assertIn("src", state["root_code_paths"])
        self.assertIn("prisma", state["root_code_paths"])
        self.assertIn("package.json", state["root_code_paths"])
        self.assertIn("src/", state["project_shape"]["formal_stack_prefixes"])
        self.assertTrue(state["adapter_rewrite_suggested"])

    def test_plan_adoption_mentions_current_v9_flow(self):
        (self.root / "src").mkdir()
        state = self.module.detect_project("demo")

        plan = self.module.plan_adoption(state)
        rendered = "\n".join(plan)

        self.assertIn("创建 adapters/demo", rendered)
        self.assertIn("--rewrite-adapter", rendered)
        self.assertIn("--apply-core", rendered)
        self.assertIn("--apply-runtime", rendered)
        self.assertIn("不自动移动", rendered)

    def test_apply_core_creates_portable_core_and_schema_v3(self):
        self.module.copy_default_adapter(
            "demo",
            force=False,
            dry_run=False,
            project_name="Demo Project",
        )

        result = self.module.copy_core_bundle(
            "demo",
            project_name="Demo Project",
            dry_run=False,
        )

        self.assertTrue(result["created"])
        self.assertTrue((self.root / "AGENTS.md").exists())
        self.assertTrue((self.root / ".gstack" / "README.md").exists())
        self.assertTrue((self.root / "scripts" / "init_project.py").exists())

        schema = json.loads(
            (self.root / "adapters" / "default" / "runtime_schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(schema["version"], 3)
        self.assertIn("online_flow_protocol", schema["required_runtime_keys"])
        self.assertIn("online_flow_protocol", schema["required_runtime_object_keys"])

    def test_apply_core_preserves_existing_files(self):
        readme = self.root / "README.md"
        readme.write_text("custom readme\n", encoding="utf-8")

        result = self.module.copy_core_bundle(
            "demo",
            project_name="Demo Project",
            dry_run=False,
        )

        self.assertIn("README.md", result["preserved_paths"])
        self.assertEqual(readme.read_text(encoding="utf-8"), "custom readme\n")

    def test_rewrite_adapter_uses_detected_project_shape(self):
        (self.root / "src").mkdir()
        (self.root / "docs").mkdir()
        (self.root / "tests").mkdir()
        self.module.copy_default_adapter(
            "demo",
            force=False,
            dry_run=False,
            project_name="Demo Project",
        )

        result = self.module.rewrite_adapter_metadata(
            "demo",
            project_name="Demo Project",
            project_shape=self.module.detect_project_shape(),
            dry_run=False,
        )

        self.assertTrue(result["changed"])
        runtime = self.read_runtime()
        self.assertIn("src/", runtime["paths"]["formal_stack_prefixes"])
        self.assertIn("docs/", runtime["paths"]["domain_spec_prefixes"])
        self.assertIn("tests/", runtime["paths"]["implementation_prefixes"])
        self.assertEqual(self.module.runtime_schema_errors("demo", runtime)[0], [])

    def test_rewrite_adapter_dry_run_does_not_change_files(self):
        self.module.copy_default_adapter(
            "demo",
            force=False,
            dry_run=False,
            project_name="Demo Project",
        )
        runtime_path = self.root / "adapters" / "demo" / "runtime.json"
        before = runtime_path.read_text(encoding="utf-8")
        (self.root / "src").mkdir()

        result = self.module.rewrite_adapter_metadata(
            "demo",
            project_name="Demo Project",
            project_shape=self.module.detect_project_shape(),
            dry_run=True,
        )

        self.assertTrue(result["would_replace"])
        self.assertEqual(runtime_path.read_text(encoding="utf-8"), before)

    def test_runtime_bundle_dry_run_reports_allowlist_without_writing(self):
        result = self.module.copy_runtime_bundle(dry_run=True)

        self.assertTrue(result["ok"])
        self.assertFalse(result["created"])
        self.assertIn(".gstack/scripts/gstack_loop.py", result["would_create"])
        self.assertFalse((self.root / ".gstack" / "scripts" / "gstack_loop.py").exists())

    def test_cli_apply_core_rewrite_and_validate_json(self):
        (self.root / "src").mkdir()
        (self.root / "docs").mkdir()

        apply_result = self.run_cli(
            "--adapter",
            "demo",
            "--project-name",
            "Demo Project",
            "--apply-core",
            "--rewrite-adapter",
            "--format",
            "json",
        )
        self.assertEqual(apply_result.returncode, 0, apply_result.stderr)
        payload = json.loads(apply_result.stdout)
        self.assertTrue(payload["apply"]["created"])
        self.assertTrue(payload["core_apply"]["created"])
        self.assertTrue(payload["rewrite"]["changed"])

        validate_result = self.run_cli(
            "--adapter",
            "demo",
            "--validate-adapter",
            "--format",
            "json",
        )
        self.assertEqual(validate_result.returncode, 0, validate_result.stdout)
        validation = json.loads(validate_result.stdout)["verification"]
        self.assertEqual(validation[0]["name"], "target-adapter-metadata")
        self.assertTrue(validation[0]["ok"])

    def test_render_report_uses_current_headings(self):
        state = self.module.detect_project("demo")

        report = self.module.render_report("demo", state)

        self.assertIn("Adapter installer detect", report)
        self.assertIn("Adapter installer plan", report)
        self.assertIn("Next safe pilot", report)
        self.assertNotIn("KK Dev Skeleton 接入报告", report)

    def test_runtime_schema_payload_matches_published_schema_version(self):
        schema = self.module.runtime_schema_payload()

        self.assertEqual(schema["version"], 3)
        self.assertIn("online_flow_protocol", schema["required_runtime_keys"])
        self.assertIn("online_flow_protocol", schema["required_runtime_object_keys"])


if __name__ == "__main__":
    unittest.main()
