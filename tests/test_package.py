import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package", ROOT / "scripts/validate_package.py")
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class MCPReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for folder in ("plugins", ".claude-plugin", ".cursor-plugin", ".grok-plugin", ".agents", ".github/plugin"):
            shutil.copytree(ROOT / folder, self.root / folder)

    def edit(self, relative, change):
        f = self.root / relative
        data = json.loads(f.read_text())
        change(data)
        f.write_text(json.dumps(data))

    def test_release_passes(self):
        self.assertGreater(package.validate(self.root), 0)

    def test_cli_hook_cannot_return_through_default_scan(self):
        hook = self.root / "plugins/ditto/hooks/hooks.json"
        hook.parent.mkdir()
        hook.write_text('{"hooks":{}}')
        with self.assertRaisesRegex(ValueError, "Unexpected release file"):
            package.validate(self.root)

    def test_marketplace_cannot_override_mcp_runtime(self):
        for relative in package.MARKETPLACES.values():
            with self.subTest(relative=relative):
                self.setUp()
                self.edit(relative, lambda d: d["plugins"][0].__setitem__("mcpServers", {"ditto": {"command": "npx"}}))
                with self.assertRaisesRegex(ValueError, "runtime override"):
                    package.validate(self.root)

    def test_credentials_and_shell_launchers_are_rejected(self):
        for relative in ("plugins/ditto/.mcp.json", "plugins/ditto/mcp.json", "plugins/ditto/mcp_config.json"):
            for field, value in (("command", "npx"), ("headers", {"Authorization": "Bearer example"})):
                with self.subTest(relative=relative, field=field):
                    self.setUp()
                    self.edit(relative, lambda d: d["mcpServers"]["ditto"].__setitem__(field, value))
                    with self.assertRaisesRegex(ValueError, "Expected hosted Ditto MCP"):
                        package.validate(self.root)

    def test_inline_host_servers_are_checked(self):
        for relative in ("plugins/ditto/.github/plugin/plugin.json", "plugins/ditto/.kimi-plugin/plugin.json"):
            with self.subTest(relative=relative):
                self.setUp()
                self.edit(relative, lambda d: d["mcpServers"]["ditto"].__setitem__("env", {"KEY": "x"}))
                with self.assertRaisesRegex(ValueError, "Expected hosted Ditto MCP"):
                    package.validate(self.root)

    def test_other_endpoint_is_rejected(self):
        f = self.root / "plugins/ditto/.mcp.json"
        f.write_text(f.read_text().replace("api.heyditto.ai", "example.com"))
        with self.assertRaisesRegex(ValueError, "Expected hosted Ditto MCP"):
            package.validate(self.root)

    def test_host_versions_must_match(self):
        self.edit("plugins/ditto/.cursor-plugin/plugin.json", lambda d: d.__setitem__("version", "9.9.9"))
        with self.assertRaisesRegex(ValueError, "share one version"):
            package.validate(self.root)

    def test_claude_marketplace_keeps_published_name(self):
        self.edit(".claude-plugin/marketplace.json", lambda d: d.__setitem__("name", "ditto-plugins"))
        with self.assertRaisesRegex(ValueError, "published name"):
            package.validate(self.root)

    def test_missing_logo_is_rejected(self):
        (self.root / "plugins/ditto/assets/logo.svg").unlink()
        with self.assertRaisesRegex(ValueError, "missing asset"):
            package.validate(self.root)

    def test_new_plugin_must_be_listed_in_every_marketplace(self):
        shutil.copytree(self.root / "plugins/ditto", self.root / "plugins/ditto-extra")
        for relative in package.MANIFESTS.values():
            self.edit(f"plugins/ditto-extra/{relative}", lambda d: d.__setitem__("name", "ditto-extra"))
        for relative in ("plugins/ditto-extra/.mcp.json", "plugins/ditto-extra/mcp.json", "plugins/ditto-extra/mcp_config.json"):
            self.edit(relative, lambda d: d.__setitem__("mcpServers", {"ditto-extra": d["mcpServers"]["ditto"]}))
        for relative in ("plugins/ditto-extra/.github/plugin/plugin.json", "plugins/ditto-extra/.kimi-plugin/plugin.json"):
            self.edit(relative, lambda d: d.__setitem__("mcpServers", {"ditto-extra": d["mcpServers"]["ditto"]}))
        with patch.dict(package.HOSTED_MCP, {"ditto-extra": "https://api.heyditto.ai/mcp"}):
            with self.assertRaisesRegex(ValueError, "listed in every marketplace"):
                package.validate(self.root)
            for host, relative in package.MARKETPLACES.items():
                def add(d):
                    entry = json.loads(json.dumps(d["plugins"][0]))
                    entry["name"] = "ditto-extra"
                    if isinstance(entry["source"], dict):
                        entry["source"]["path"] = "./plugins/ditto-extra"
                    else:
                        entry["source"] = "./plugins/ditto-extra"
                    d["plugins"].append(entry)
                self.edit(relative, add)
                if host == "claude":
                    with self.assertRaisesRegex(ValueError, "different plugins"):
                        package.validate(self.root)
            self.assertGreater(package.validate(self.root), 0)


if __name__ == "__main__":
    unittest.main()
