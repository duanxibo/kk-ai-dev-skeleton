import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read_doc(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


class MarketplaceRolloutDocsTest(unittest.TestCase):
    def test_rollout_docs_exist(self):
        for path in [
            "plugins/MARKETPLACE_ROLLOUT.md",
            "plugins/ADMIN_INSTALL_CHECKLIST.md",
            "plugins/PILOT_FEEDBACK.md",
        ]:
            self.assertTrue((REPO_ROOT / path).is_file(), path)

    def test_rollout_doc_names_marketplace_and_plugin(self):
        content = read_doc("plugins/MARKETPLACE_ROLLOUT.md")

        self.assertIn("kk-dev-skeleton-internal", content)
        self.assertIn("kk-dev-skeleton-adoption", content)
        self.assertIn("自然语言", content)
        self.assertIn("管理员", content)
        self.assertIn("PILOT_FEEDBACK.md", content)

    def test_admin_checklist_keeps_install_as_admin_action(self):
        content = read_doc("plugins/ADMIN_INSTALL_CHECKLIST.md")

        self.assertIn("明确授权", content)
        self.assertIn(
            "codex plugin marketplace add https://github.com/duanxibo/kk-ai-dev-skeleton.git --ref main",
            content,
        )
        self.assertIn(
            "codex plugin add kk-dev-skeleton-adoption@kk-dev-skeleton-internal",
            content,
        )
        self.assertIn("普通业务用户不需要执行这里的命令", content)

    def test_feedback_form_captures_pilot_risks(self):
        content = read_doc("plugins/PILOT_FEEDBACK.md")

        self.assertIn("是否出现命令行优先引导", content)
        self.assertIn("是否默认触碰真实数据、生产、数据库或 git workflow action", content)
        self.assertIn("决策：继续 / 暂停 / 回滚 / 扩大", content)

    def test_entry_docs_link_rollout_package(self):
        for path in [
            "README.md",
            "COMPANY_ADOPTION_GUIDE.md",
            "CODEX_ADOPTION_CONNECTOR.md",
            "plugins/MARKETPLACE_INSTALL.md",
            "plugins/README.md",
            ".agents/plugins/README.md",
        ]:
            content = read_doc(path)
            self.assertIn("MARKETPLACE_ROLLOUT.md", content, path)


if __name__ == "__main__":
    unittest.main()
