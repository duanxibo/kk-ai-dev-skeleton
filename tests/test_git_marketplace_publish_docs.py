import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GIT_URL = "https://github.com/duanxibo/kk-ai-dev-skeleton.git"
MARKETPLACE_NAME = "kk-dev-skeleton-internal"
PLUGIN_NAME = "kk-dev-skeleton-adoption"


def read_doc(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


class GitMarketplacePublishDocsTest(unittest.TestCase):
    def test_partner_install_doc_has_copy_ready_prompt(self):
        content = read_doc("plugins/PARTNER_INSTALL.md")

        self.assertIn(GIT_URL, content)
        self.assertIn(MARKETPLACE_NAME, content)
        self.assertIn(PLUGIN_NAME, content)
        self.assertIn("请帮我安装 KK Dev Skeleton 的 Codex plugin", content)
        self.assertIn("不要连接真实数据、生产环境、数据库", content)

    def test_partner_install_doc_has_equivalent_codex_commands(self):
        content = read_doc("plugins/PARTNER_INSTALL.md")

        self.assertIn(f"codex plugin marketplace add {GIT_URL} --ref main", content)
        self.assertIn(f"codex plugin add {PLUGIN_NAME}@{MARKETPLACE_NAME}", content)
        self.assertIn(f"codex plugin marketplace upgrade {MARKETPLACE_NAME}", content)

    def test_entry_docs_reference_published_git_marketplace(self):
        for path in [
            "README.md",
            "COMPANY_ADOPTION_GUIDE.md",
            "CODEX_ADOPTION_CONNECTOR.md",
            "plugins/MARKETPLACE_INSTALL.md",
            "plugins/MARKETPLACE_ROLLOUT.md",
            "plugins/ADMIN_INSTALL_CHECKLIST.md",
            "plugins/README.md",
            ".agents/plugins/README.md",
        ]:
            self.assertIn(GIT_URL, read_doc(path), path)

    def test_partner_install_is_linked_from_rollout_docs(self):
        for path in [
            "README.md",
            "plugins/MARKETPLACE_INSTALL.md",
            "plugins/MARKETPLACE_ROLLOUT.md",
            "plugins/README.md",
            ".agents/plugins/README.md",
        ]:
            self.assertIn("PARTNER_INSTALL.md", read_doc(path), path)


if __name__ == "__main__":
    unittest.main()
