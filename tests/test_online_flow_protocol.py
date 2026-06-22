import importlib.util
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGN_DOC = REPO_ROOT / ".gstack" / "designs" / "2026-06-22_online-software-factory-platform-protocol.md"
RUNTIME_JSON = REPO_ROOT / "adapters" / "default" / "runtime.json"
RUNTIME_SCHEMA = REPO_ROOT / "adapters" / "default" / "runtime_schema.json"
ADAPTER_MD = REPO_ROOT / "adapters" / "default" / "adapter.md"
PLUGIN_README = REPO_ROOT / "plugins" / "kk-dev-skeleton-adoption" / "README.md"
PLUGIN_SKILL = (
    REPO_ROOT
    / "plugins"
    / "kk-dev-skeleton-adoption"
    / "skills"
    / "kk-dev-skeleton-adoption"
    / "SKILL.md"
)
INIT_PROJECT = REPO_ROOT / "scripts" / "init_project.py"


def load_init_project_module():
    spec = importlib.util.spec_from_file_location("init_project_online_flow", INIT_PROJECT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["init_project_online_flow"] = module
    spec.loader.exec_module(module)
    return module


class OnlineFlowProtocolTest(unittest.TestCase):
    def test_protocol_design_defines_platform_runner_repo_contract(self):
        text = DESIGN_DOC.read_text(encoding="utf-8")

        for token in (
            "OnlineDemand",
            "MvpConfirmation",
            "ClaimPackage",
            "StatusEvent",
            "Codex Runner",
            "Repo Skeleton",
            "Evidence Mapping",
            "授权协议",
        ):
            self.assertIn(token, text)

        self.assertIn("repo-native evidence", text)
        self.assertIn("必须单独授权", text)
        self.assertIn("不托管 Web 平台状态数据库", text)

    def test_default_runtime_declares_online_flow_protocol(self):
        runtime = json.loads(RUNTIME_JSON.read_text(encoding="utf-8"))
        online_flow = runtime["online_flow_protocol"]

        self.assertEqual(runtime["version"], 7)
        self.assertEqual(online_flow["protocol_version"], "online-flow-v1")
        self.assertEqual(online_flow["status"], "supported")
        self.assertEqual(
            online_flow["design_doc"],
            ".gstack/designs/2026-06-22_online-software-factory-platform-protocol.md",
        )
        self.assertIn("OnlineDemand", online_flow["objects"])
        self.assertIn("ClaimPackage", online_flow["objects"])
        self.assertIn("StatusEvent", online_flow["objects"])
        self.assertIn("ClaimPackage", online_flow["evidence_mapping"])
        self.assertIn("git workflow", " ".join(online_flow["requires_separate_authorization"]))
        self.assertIn("does not implement the web platform", online_flow["non_actions"])

    def test_runtime_schema_requires_online_flow_protocol(self):
        schema = json.loads(RUNTIME_SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(schema["version"], 3)
        self.assertIn("online_flow_protocol", schema["required_runtime_keys"])
        self.assertIn("online_flow_protocol", schema["required_runtime_object_keys"])

    def test_installer_generated_runtime_includes_online_flow_protocol(self):
        module = load_init_project_module()
        runtime = module.runtime_payload("demo", project_name="Demo")
        errors, warnings = module.runtime_schema_errors("demo", runtime)

        self.assertEqual(errors, [])
        self.assertIn("online_flow_protocol", runtime)
        self.assertEqual(runtime["online_flow_protocol"]["status"], "supported")
        self.assertIn("OnlineDemand", runtime["online_flow_protocol"]["objects"])
        self.assertIn("StatusEvent", runtime["online_flow_protocol"]["evidence_mapping"])
        self.assertIsInstance(warnings, list)

    def test_public_online_flow_docs_do_not_leak_project_specific_context(self):
        forbidden = [
            "Tian" + "Gong",
            "tian" + "gong",
            "天" + "宫",
            "t" + "g-",
            "/" + "Users/",
            "Click" + "House",
            "Meta" + "base",
        ]
        paths = [
            DESIGN_DOC,
            ADAPTER_MD,
            PLUGIN_README,
            PLUGIN_SKILL,
            REPO_ROOT / ".gstack" / "requirements" / "2026-06-22_online-software-factory-readiness-standard-requirement.md",
            REPO_ROOT / ".gstack" / "reviews" / "2026-06-22_online-software-factory-readiness-standard-review.md",
            REPO_ROOT / ".gstack" / "task-boundaries" / "2026-06-22_online-software-factory-readiness.md",
        ]

        offenders = []
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                if token in text:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}: {token}")

        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
