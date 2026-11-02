#!/usr/bin/env python3
"""Check the MCP-only, multi-host plugin release boundary without connecting an account.

`--archive <zip outside the repository>` also writes and byte-verifies the ChatGPT
directory upload: plugins/ditto/.openai-plugin/plugin.json as ditto/plugin.json,
with mcp.json, README, assets and skills.

Every root marketplace must list the same plugins. Each plugin lives in
plugins/<name>/ with one manifest per host, one shared skills/ folder and
hosted-MCP configuration only: no launchers, credentials, hooks, commands or
agents.
"""
import argparse
import json
import re
import zipfile
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
    # ChatGPT reads a portable Agent Plugins manifest, with its listing under
    # extensions["com.openai"], at the root of its upload. Kept out of the plugin
    # root here because Grok prefers a root plugin.json over .grok-plugin/.
    "openai": ".openai-plugin/plugin.json",
}
# Hosts that install a GitHub URL only from the repository root get a root
# manifest that points into one plugin. Kimi Code reads <repo>/.kimi-plugin/plugin.json.
ROOT_MANIFESTS = {".kimi-plugin/plugin.json": ("kimi", "ditto")}
MCP_FILES = {".mcp.json": "type", "mcp.json": "type", "mcp_config.json": None}
# Antigravity loads a manifest that declares the portable Agent Plugins schema as
# an Agent Plugins package: it then treats .mcp.json and mcp.json as other hosts'
# files instead of warning that they are "never loaded", which keeps
# `agy plugin validate --strict` clean. Its native mode still reads
# mcp_config.json; with enable-agent-plugins-spec on it reads mcp.json.
AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AGENT_PLUGINS_MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
# Each plugin's only permitted MCP endpoint. Add an entry when adding a plugin.
HOSTED_MCP = {"ditto": "https://api.heyditto.ai/mcp"}
RUNTIME = {"hooks", "commands", "agents", "userConfig", "settings", "lspServers", "apps"}
ALLOWED_FILES = {*MANIFESTS.values(), *MCP_FILES, "README.md", "shared-skills.lock.json"}
TEXT = {".md", ".json", ".yaml", ".yml", ".txt"}
ASSETS = {".png", ".svg"}
SERVER_KEYS = {"type", "transport", "url", "serverUrl"}
REPOSITORY = "https://github.com/ditto-assistant/ditto-plugins"


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
    urls = [server[k] for k in ("url", "serverUrl") if k in server]
    url = urls[0] if len(urls) == 1 else None
    kind = server.get("type", server.get("transport", "http"))
    if expected is None or url != expected or name != plugin or kind not in {"http", "streamable-http"}:
        raise ValueError("Expected hosted Ditto MCP without launcher, headers or credentials")


def check_mcp_file(path, plugin):
    data = load(path)
    if set(data) - {"$schema", "mcpServers"} or not isinstance(data.get("mcpServers"), dict) or len(data["mcpServers"]) != 1:
        raise ValueError("Expected hosted Ditto MCP without launcher, headers or credentials")
    if Path(path).name == "mcp.json" and data.get("$schema") != AGENT_PLUGINS_MCP_SCHEMA:
        raise ValueError("mcp.json is the portable Agent Plugins MCP file (Codex, Antigravity) and must declare its $schema")
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
    if host == "openai":
        def obj(value):
            return value if isinstance(value, dict) else {}
        listing = obj(obj(manifest.get("extensions")).get("com.openai"))
        ui = listing.get("interface")
        if manifest.get("$schema") != AGENT_PLUGINS_SCHEMA or not isinstance(ui, dict):
            raise ValueError("openai manifest must be a portable Agent Plugins manifest with extensions.com.openai.interface")
        if manifest.get("repository") != REPOSITORY:
            raise ValueError(f"openai manifest repository must be {REPOSITORY}")
        # Directory listing limits (docs/openai/listing-fields-and-engineering-handoff.md).
        limits = {"displayName": 30, "shortDescription": 30, "longDescription": 4000}
        if any(not isinstance(ui.get(k), str) or not ui[k].strip() or len(ui[k]) > n for k, n in limits.items()):
            raise ValueError("openai listing needs displayName and shortDescription of at most 30 characters and a longDescription of at most 4000")
        prompts = ui.get("defaultPrompt", [])
        if not isinstance(prompts, list) or any(not isinstance(x, str) or not x.strip() or len(x) > 128 for x in prompts) or len(prompts) > 3 or len(set(prompts)) != len(prompts):
            raise ValueError("openai listing allows up to 3 unique starter prompts of at most 128 characters")
        cases = obj(obj(listing.get("review")).get("test_cases"))
        for category, required in (("positive", ("description", "prompt", "tools_triggered", "expected_behavior")), ("negative", ("description", "prompt"))):
            entries = cases.get(category)
            if not isinstance(entries, list) or not entries or any(not isinstance(c, dict) or not all(isinstance(c.get(k), str) and c[k].strip() for k in required) for c in entries):
                raise ValueError(f"openai review needs complete {category} test cases")
    if host == "antigravity":
        if manifest.get("$schema") != AGENT_PLUGINS_SCHEMA:
            raise ValueError("antigravity manifest must declare the Agent Plugins $schema (agy --strict warns on other hosts' MCP files otherwise)")
        if "skills" in manifest:
            raise ValueError("antigravity manifest must not set skills: agy ignores it in Agent Plugins mode and --strict fails; skills/ loads either way")
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
    if host == "openai":
        interface = ui
    for key in ("icon", "logo"):
        for value in (manifest.get(key), interface.get(key), interface.get("composerIcon")):
            if isinstance(value, str) and not (folder / value).is_file():
                raise ValueError(f"{host} manifest references a missing asset: {value}")
    for value in ([manifest.get("skills")] if isinstance(manifest.get("skills"), str) else manifest.get("skills") or []):
        if value.rstrip("/") not in {"./skills", "skills"}:
            raise ValueError(f"{host} manifest must use the shared skills folder")


def check_root_manifest(root, relative, host, plugin):
    """A root manifest is the plugin's own host manifest with paths rebased into plugins/<name>."""
    path = root / relative
    parts = Path(relative).parts
    if any((root / Path(*parts[:i])).is_symlink() for i in range(1, len(parts) + 1)):
        raise ValueError("Linked release input")
    if not path.is_file():
        raise ValueError(f"Missing root {host} manifest {relative}")
    manifest = load(path)
    expected = load(root / "plugins" / plugin / MANIFESTS[host])
    expected["skills"] = [f"./plugins/{plugin}/skills"]
    if manifest != expected:
        raise ValueError(f"Root {relative} must equal plugins/{plugin}/{MANIFESTS[host]} with skills ./plugins/{plugin}/skills")


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
    for relative, (host, plugin) in ROOT_MANIFESTS.items():
        check_root_manifest(root, relative, host, plugin)
    for name in ("ditto-memory", "curate-music", "handoff"):
        if not (root / "plugins/ditto/skills" / name / "SKILL.md").is_file():
            raise ValueError(f"Missing skill: {name}")
    return count


def openai_upload(root, plugin="ditto"):
    """The files ChatGPT reads; other hosts' manifests stay out of the upload."""
    folder = root / "plugins" / plugin
    upload = {"plugin.json": folder / MANIFESTS["openai"]}
    for f in [folder / "mcp.json", folder / "README.md", *sorted(p for d in ("assets", "skills") for p in (folder / d).rglob("*") if p.is_file())]:
        upload[f.relative_to(folder).as_posix()] = f
    return folder, upload


def archive(root, output):
    validate(root)
    folder, upload = openai_upload(root)
    output = Path(output).resolve()
    if output.is_relative_to(Path(root).resolve()):
        raise ValueError("Archive must be written outside the repository")
    names = {f"{folder.name}/{name}": f for name, f in upload.items()}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name, f in names.items():
            bundle.write(f, name)
    with zipfile.ZipFile(output) as bundle:
        if bundle.testzip() is not None or set(bundle.namelist()) != set(names) or any(bundle.read(n) != f.read_bytes() for n, f in names.items()):
            raise ValueError("Archive differs from validated source")
    return output, len(names)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--archive", type=Path, help="write the ChatGPT directory upload ZIP here (outside the repository)")
    args = parser.parse_args()
    print(f"MCP-only multi-host package verified: {validate(ROOT)} files")
    if args.archive:
        path, count = archive(ROOT, args.archive)
        print(f"ChatGPT upload verified: {path} ({count} files). Host behavior and submission readiness remain unverified.")
