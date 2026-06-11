import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "kk-dev-skeleton-adoption"


class PluginMarketplaceTest(unittest.TestCase):
    def load_marketplace(self):
        return json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))

    def test_marketplace_shape(self):
        payload = self.load_marketplace()

        self.assertEqual(payload["name"], "kk-dev-skeleton-internal")
        self.assertEqual(
            payload["interface"]["displayName"],
            "KK Dev Skeleton Internal",
        )
        self.assertIsInstance(payload["plugins"], list)
        self.assertEqual(len(payload["plugins"]), 1)

    def test_plugin_entry_points_to_repo_local_source(self):
        entry = self.load_marketplace()["plugins"][0]

        self.assertEqual(entry["name"], "kk-dev-skeleton-adoption")
        self.assertEqual(entry["source"], {
            "source": "local",
            "path": "./plugins/kk-dev-skeleton-adoption",
        })
        self.assertTrue((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").is_file())
        self.assertTrue(
            (PLUGIN_ROOT / "skills" / "kk-dev-skeleton-adoption" / "SKILL.md").is_file()
        )

    def test_plugin_entry_has_required_policy(self):
        entry = self.load_marketplace()["plugins"][0]

        self.assertEqual(entry["policy"], {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        })
        self.assertEqual(entry["category"], "Productivity")

    def test_marketplace_does_not_use_product_override(self):
        entry = self.load_marketplace()["plugins"][0]

        self.assertNotIn("products", entry["policy"])


if __name__ == "__main__":
    unittest.main()
