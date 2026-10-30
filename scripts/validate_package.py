#!/usr/bin/env python3
"""Check the MCP-only, multi-host plugin release boundary without connecting an account.

Every root marketplace must list the same plugins. Each plugin lives in
plugins/<name>/ with one manifest per host, one shared skills/ folder and
hosted-MCP configuration only: no launchers, credentials, hooks, commands or
agents.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE_MARKETPLACE_NAME = "ditto-claude-plugins"  # keep: existing installs track this name
MARKETPLACES = {
    "claude": ".claude-plugin/marketplace.json",
    "cursor": ".cursor-plugin/marketplace.json",
    "grok": ".grok-plugin/marketplace.json",
    "codex": ".agents/plugins/marketplace.json",
    "copilot": ".github/plugin/marketplace.json",
}
MANIFESTS = {
    "claude": ".claude-plugin/plugin.json",
    "cursor": ".cursor-plugin/plugin.json",
    "grok": ".grok-plugin/plugin.json",
    "codex": ".codex-plugin/plugin.json",
    "copilot": ".github/plugin/plugin.json",
    "antigravity": ".antigravity-plugin/plugin.json",
    "kimi": ".kimi-plugin/plugin.json",
}
MCP_FILES = {".mcp.json": "type", "mcp.json": "type", "mcp_config.json": None}
# Each plugin's only permitted MCP endpoint. Add an entry when adding a plugin.
HOSTED_MCP = {"ditto": "https://api.heyditto.ai/mcp"}
RUNTIME = {"hooks", "commands", "agents", "userConfig", "settings", "lspServers", "apps"}
ALLOWED_FILES = {*MANIFESTS.values(), *MCP_FILES, "README.md", "shared-skills.lock.json"}
TEXT = {".md", ".json", ".yaml", ".yml", ".txt"}
ASSETS = {".png", ".svg"}
SERVER_KEYS = {"type", "transport", "url", "serverUrl"}


def load(path):
    return json.loads(Path(path).read_text())


def plugin_dir(root, entry):
    source = entry.get("source")
    if isinstance(source, dict):
        source = source.get("path")
    if not isinstance(source, str) or not re.fullmatch(r"\./plugins/[a-z0-9]+(?:-[a-z0-9]+)*", source):
        raise ValueError(f"Unexpected marketplace source: {source!r}")
    if source != f"./plugins/{entry.get('name')}":
        raise ValueError("Marketplace entry name must match its plugins/<name> folder")
    return root / source


def check_server(name, server, plugin):
    """A hosted server declaration: URL plus transport only."""
    expected = HOSTED_MCP.get(plugin)
    if not isinstance(server, dict) or set(server) - SERVER_KEYS:
        raise ValueError("Expected hosted Ditto MCP without launcher, headers or credentials")
    url = server.get("url", server.get("serverUrl"))
    kind = server.get("type", server.get("transport", "http"))
    if expected is None or url != expected or name != plugin or kind not in {"http", "streamable-http"}:
        raise ValueError("Expected hosted Ditto MCP without launcher, headers or credentials")


def check_mcp_file(path, plugin):
    data = load(path)
    if set(data) - {"$schema", "mcpServers"} or not isinstance(data.get("mcpServers"), dict) or len(data["mcpServers"]) != 1:
        raise ValueError("Expected hosted Ditto MCP without launcher, headers or credentials")
    for name, server in data["mcpServers"].items():
        check_server(name, server, plugin)


def check_manifest(host, manifest, plugin, folder):
    if manifest.get("name") != plugin:
        raise ValueError(f"{host} manifest name must be {plugin}")
    if RUNTIME & manifest.keys():
        raise ValueError(f"Unexpected runtime component in MCP-only {host} manifest")
    mcp = manifest.get("mcpServers")
    if host == "claude" and mcp is not None:
        raise ValueError("Unexpected runtime component in MCP-only claude manifest")  # Claude loads .mcp.json itself
    if isinstance(mcp, str):
        if mcp not in {"./.mcp.json", "./mcp.json"} or not (folder / mcp).is_file():
            raise ValueError(f"{host} manifest must point at the bundled MCP file")
    elif isinstance(mcp, dict):
        if len(mcp) != 1:
            raise ValueError("Expected hosted Ditto MCP without launcher, headers or credentials")
        for name, server in mcp.items():
            check_server(name, server, plugin)
    elif mcp is not None:
        raise ValueError(f"Unexpected mcpServers in {host} manifest")
    interface = manifest.get("interface") if isinstance(manifest.get("interface"), dict) else {}
    for key in ("icon", "logo"):
        for value in (manifest.get(key), interface.get(key), interface.get("composerIcon")):
            if isinstance(value, str) and not (folder / value).is_file():
                raise ValueError(f"{host} manifest references a missing asset: {value}")
    for value in ([manifest.get("skills")] if isinstance(manifest.get("skills"), str) else manifest.get("skills") or []):
        if value.rstrip("/") not in {"./skills", "skills"}:
            raise ValueError(f"{host} manifest must use the shared skills folder")


def validate(root):
    root = Path(root)
    lists = {}
    for host, relative in MARKETPLACES.items():
        catalog = load(root / relative)
        entries = catalog.get("plugins", [])
        if not entries:
            raise ValueError(f"Empty {host} marketplace")
        for entry in entries:
            if RUNTIME & entry.keys() or "mcpServers" in entry:
                raise ValueError("Unexpected marketplace source or runtime override")
            plugin_dir(root, entry)
        lists[host] = sorted(e["name"] for e in entries)
        if len(set(lists[host])) != len(lists[host]):
            raise ValueError(f"Duplicate plugin in {host} marketplace")
    if load(root / MARKETPLACES["claude"]).get("name") != CLAUDE_MARKETPLACE_NAME:
        raise ValueError("Claude marketplace must keep its published name")
    if len({tuple(v) for v in lists.values()}) != 1:
        raise ValueError(f"Marketplaces list different plugins: {lists}")
    on_disk = sorted(p.name for p in (root / "plugins").iterdir() if p.is_dir())
    if on_disk != lists["claude"]:
        raise ValueError("Every plugins/<name> folder must be listed in every marketplace")
    count = 0
    for plugin in lists["claude"]:
        folder = root / "plugins" / plugin
        versions = set()
        for host, relative in MANIFESTS.items():
            path = folder / relative
            if not path.is_file():
                raise ValueError(f"Missing {host} manifest for {plugin}")
            manifest = load(path)
            check_manifest(host, manifest, plugin, folder)
            versions.add(manifest.get("version"))
        if len(versions) != 1 or None in versions:
            raise ValueError(f"Host manifests for {plugin} must share one version")
        for name in MCP_FILES:
            if not (folder / name).is_file():
                raise ValueError(f"Missing {name} for {plugin}")
            check_mcp_file(folder / name, plugin)
        for item in folder.rglob("*"):
            if item.is_symlink():
                raise ValueError("Linked release input")
            if not item.is_file():
                continue
            count += 1
            relative = item.relative_to(folder)
            ok = (relative.as_posix() in ALLOWED_FILES
                  or (relative.parts[0] == "skills" and item.suffix in TEXT)
                  or (relative.parts[0] == "assets" and len(relative.parts) == 2 and item.suffix in ASSETS))
            if not ok:
                raise ValueError(f"Unexpected release file: {relative}")
        if not any((folder / "skills").glob("*/SKILL.md")):
            raise ValueError(f"{plugin} ships no skills")
    for name in ("ditto-memory", "curate-music", "handoff"):
        if not (root / "plugins/ditto/skills" / name / "SKILL.md").is_file():
            raise ValueError(f"Missing skill: {name}")
    return count


if __name__ == "__main__":
    print(f"MCP-only multi-host package verified: {validate(ROOT)} files")
