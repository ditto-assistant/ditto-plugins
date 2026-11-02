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
        for folder in ("plugins", ".claude-plugin", ".cursor-plugin", ".grok-plugin", ".agents", ".github/plugin", ".kimi-plugin"):
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

    def test_http_url_is_rejected(self):
        # Only the retired Gemini CLI read httpUrl; any other host given one installs without MCP.
        for relative in ("plugins/ditto/.mcp.json", "plugins/ditto/mcp_config.json", "plugins/ditto/.kimi-plugin/plugin.json"):
            with self.subTest(relative=relative):
                self.setUp()
                self.edit(relative, lambda d: d["mcpServers"].__setitem__("ditto", {"httpUrl": "https://api.heyditto.ai/mcp"}))
                with self.assertRaisesRegex(ValueError, "Expected hosted Ditto MCP"):
                    package.validate(self.root)

    def test_antigravity_manifest_loads_as_agent_plugins_package(self):
        # Without the portable $schema, agy warns that .mcp.json and mcp.json are
        # never loaded and `agy plugin validate --strict` fails (DITTO-1800).
        relative = "plugins/ditto/.antigravity-plugin/plugin.json"
        for change, message in ((lambda d: d.pop("$schema"), "Agent Plugins \\$schema"),
                                (lambda d: d.__setitem__("skills", ["./skills"]), "must not set skills")):
            with self.subTest(message=message):
                self.setUp()
                self.edit(relative, change)
                with self.assertRaisesRegex(ValueError, message):
                    package.validate(self.root)

    def test_portable_mcp_file_declares_its_schema(self):
        self.edit("plugins/ditto/mcp.json", lambda d: d.pop("$schema"))
        with self.assertRaisesRegex(ValueError, "portable Agent Plugins MCP file"):
            package.validate(self.root)

    def test_root_kimi_manifest_points_into_the_plugin(self):
        # Kimi Code installs a GitHub URL from the repository root only (DITTO-1799).
        cases = (
            (lambda d: d.__setitem__("skills", ["./skills"]), "skills ./plugins/ditto/skills"),
            (lambda d: d.__setitem__("version", "9.9.9"), "must equal"),
            (lambda d: d["mcpServers"]["ditto"].__setitem__("url", "https://example.com/mcp"), "must equal"),
        )
        for change, message in cases:
            with self.subTest(message=message):
                self.setUp()
                self.edit(".kimi-plugin/plugin.json", change)
                with self.assertRaisesRegex(ValueError, message):
                    package.validate(self.root)
        self.setUp()
        (self.root / ".kimi-plugin/plugin.json").unlink()
        with self.assertRaisesRegex(ValueError, "Missing root kimi manifest"):
            package.validate(self.root)
        self.setUp()
        linked = self.root / ".kimi-plugin/plugin.json"
        target = self.root / "kimi-root.json"
        target.write_text(linked.read_text())
        linked.unlink()
        linked.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "Linked release input"):
            package.validate(self.root)
        self.setUp()
        folder = self.root / ".kimi-plugin"
        outside = Path(self.tmp.name + "-outside")
        shutil.copytree(folder, outside)
        self.addCleanup(shutil.rmtree, outside)
        shutil.rmtree(folder)
        folder.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Linked release input"):
            package.validate(self.root)

    def test_openai_manifest_is_a_portable_listing_of_this_repository(self):
        relative = "plugins/ditto/.openai-plugin/plugin.json"
        listing = lambda d: d["extensions"]["com.openai"]["interface"]
        cases = (
            (lambda d: d.pop("$schema"), "portable Agent Plugins"),
            (lambda d: d["extensions"].pop("com.openai"), "portable Agent Plugins"),
            (lambda d: d.__setitem__("repository", "https://github.com/ditto-assistant/ditto-openai-plugins"), "repository must be"),
            (lambda d: listing(d).__setitem__("shortDescription", "x" * 31), "30"),
            (lambda d: listing(d).__setitem__("defaultPrompt", ["a", "b", "c", "d"]), "starter prompts"),
            (lambda d: listing(d).__setitem__("defaultPrompt", ["x" * 129]), "starter prompts"),
            (lambda d: listing(d).__setitem__("logo", "./assets/ditto-icon.png"), "missing asset"),
            (lambda d: d.__setitem__("version", "9.9.9"), "share one version"),
        )
        for change, message in cases:
            with self.subTest(message=message):
                self.setUp()
                self.edit(relative, change)
                with self.assertRaisesRegex(ValueError, message):
                    package.validate(self.root)
        self.setUp()
        (self.root / relative).unlink()
        with self.assertRaisesRegex(ValueError, "Missing openai manifest"):
            package.validate(self.root)

    def test_chatgpt_upload_carries_only_the_openai_package(self):
        import zipfile
        out = Path(self.tmp.name).parent / f"{Path(self.tmp.name).name}-upload.zip"
        self.addCleanup(out.unlink, missing_ok=True)
        _, count = package.archive(self.root, out)
        names = zipfile.ZipFile(out).namelist()
        self.assertEqual(count, len(names))
        self.assertIn("ditto/plugin.json", names)
        self.assertIn("ditto/skills/ditto-memory/SKILL.md", names)
        self.assertFalse([n for n in names if "/." in n], "other hosts' manifests must stay out of the upload")
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            package.archive(self.root, self.root / "ditto.zip")

    def test_runtime_directories_are_not_release_files(self):
        for folder in ("commands", "hooks", "policies", "agents"):
            with self.subTest(folder=folder):
                self.setUp()
                extra = self.root / "plugins/ditto" / folder / "x.toml"
                extra.parent.mkdir()
                extra.write_text("prompt = 'x'\n")
                with self.assertRaisesRegex(ValueError, "Unexpected release file"):
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
