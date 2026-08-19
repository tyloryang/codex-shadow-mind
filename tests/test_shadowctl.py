from __future__ import annotations

import json
import tempfile
import tomllib
import unittest
from pathlib import Path

import shadowctl


class ShadowCtlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name) / ".codex"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_install_is_idempotent_and_preserves_existing_config(self) -> None:
        self.home.mkdir()
        (self.home / "config.toml").write_text('model = "example"\n', encoding="utf-8")
        shadowctl.install(self.home)
        shadowctl.install(self.home)

        config = (self.home / "config.toml").read_text(encoding="utf-8")
        self.assertIn('model = "example"', config)
        self.assertEqual(config.count(shadowctl.CONFIG_START), 1)
        parsed = tomllib.loads(config)
        self.assertEqual(parsed["agents"]["code_auditor"]["config_file"], "agents/code_auditor.toml")
        self.assertTrue(shadowctl.status(self.home)["enabled"])

    def test_installed_agent_toml_is_parseable(self) -> None:
        shadowctl.install(self.home)
        for name in shadowctl.AUDITOR_NAMES:
            data = tomllib.loads((self.home / "agents" / f"{name}.toml").read_text(encoding="utf-8"))
            self.assertEqual(data["sandbox_mode"], "read-only")
            self.assertTrue(data["developer_instructions"].strip())

    def test_disable_and_enable_only_toggle_guidance(self) -> None:
        shadowctl.install(self.home)
        shadowctl.disable(self.home)
        self.assertFalse(shadowctl.status(self.home)["enabled"])
        self.assertTrue(shadowctl.status(self.home)["installed"])
        shadowctl.enable(self.home)
        self.assertTrue(shadowctl.status(self.home)["enabled"])

    def test_conflicting_agent_definition_is_rejected(self) -> None:
        self.home.mkdir()
        (self.home / "config.toml").write_text("[agents.code_auditor]\ndescription = 'mine'\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            shadowctl.install(self.home)

    def test_uninstall_preserves_user_content_and_modified_agent(self) -> None:
        self.home.mkdir()
        (self.home / "AGENTS.md").write_text("# My rules\n", encoding="utf-8")
        shadowctl.install(self.home)
        custom = self.home / "agents" / "code_auditor.toml"
        custom.write_text(custom.read_text(encoding="utf-8") + "\n# customized\n", encoding="utf-8")
        preserved = shadowctl.uninstall(self.home)

        self.assertIn("# My rules", (self.home / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertTrue(custom.exists())
        self.assertIn(str(custom), preserved)
        self.assertFalse((self.home / "agents" / "goal_auditor.toml").exists())

    def test_status_shape(self) -> None:
        shadowctl.install(self.home)
        result = shadowctl.status(self.home)
        json.dumps(result)
        self.assertEqual(set(result["auditors"]), set(shadowctl.AUDITOR_NAMES))

    def test_installed_controller_can_sync_its_own_payload(self) -> None:
        shadowctl.install(self.home)
        installed_root = self.home / "shadow-mind"
        original = shadowctl.source_root
        try:
            shadowctl.source_root = lambda: installed_root
            shadowctl.install(self.home)
        finally:
            shadowctl.source_root = original
        self.assertTrue(shadowctl.status(self.home)["installed"])


if __name__ == "__main__":
    unittest.main()
