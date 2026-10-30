#!/usr/bin/env python3
"""Build public-safe skill text; verify vendored releases without private access.

A distribution repository holds one or more plugins under ``plugins/<name>/``.
Each plugin receives one skill catalog. A plugin may declare one adapted skill
whose generated SKILL.md is the canonical core plus that distribution's
host-connection adapter. The ``plugins`` host is the multi-host monorepo
(ditto-assistant/ditto-plugins): one shared skills folder per plugin serves
Claude, Cursor, Grok, Codex, Copilot, Antigravity and Kimi manifests, so every
versioned manifest in the plugin directory is bumped together.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

SOURCE_REPOSITORY = "https://github.com/ditto-assistant/ditto-skills"
DEFAULT_PLUGIN = "ditto"
DEFAULT_ADAPTED = "ditto-memory"
CORE = "skills/ditto-memory/SKILL.md"
ADAPTER = "adapters/ditto-memory.md"
OUTPUT = "plugins/ditto/skills/ditto-memory/SKILL.md"
LOCK = "plugins/ditto/shared-skills.lock.json"
GENERATOR = "scripts/shared_skills.py"
REGISTRY = "scripts/plugins.json"
MARKER = b"\n<!-- ditto-shared-core:end -->\n\n"
NAME = r"[a-z0-9]+(?:-[a-z0-9]+)*"
# Versioned manifests, relative to plugins/<name>/. The first entry is required.
PLUGIN_MANIFESTS = {
    "openai": ["plugin.json"],
    "claude": [".claude-plugin/plugin.json"],
    "plugins": [
        ".claude-plugin/plugin.json",
        ".cursor-plugin/plugin.json",
        ".grok-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        "plugin.json",
        ".github/plugin/plugin.json",
        ".antigravity-plugin/plugin.json",
        ".kimi-plugin/plugin.json",
    ],
}
MANIFESTS = {host: f"plugins/{DEFAULT_PLUGIN}/{paths[0]}" for host, paths in PLUGIN_MANIFESTS.items()}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def file_at(root, relative):
    root = Path(root).resolve()
    value = root / relative
    if Path(relative).is_absolute() or not value.resolve().is_relative_to(root):
        raise ValueError("Path escapes repository")
    for item in [value, *value.parents]:
        if item == root:
            break
        if item.is_symlink():
            raise ValueError("Symlinks are not release inputs or outputs")
    return value


def public_text(value):
    text = value.decode("utf-8")
    if re.search(r"/Users/|/home/|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]+|ditto_mcp_[A-Za-z0-9]{8,}", text):
        raise ValueError("Private host path or credential in release text")
    if b"\r" in value or not value.endswith(b"\n") or MARKER in value:
        raise ValueError("Expected canonical LF text with one trailing newline and no generated marker")
    return value


def source_identity(source):
    status = subprocess.check_output(["git", "-C", str(source), "status", "--porcelain", "--untracked-files=all"], text=True)
    if status:
        raise ValueError("Commit canonical source before generating a release")
    return subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()


def layout(plugin=DEFAULT_PLUGIN, adapted=DEFAULT_ADAPTED):
    """Repository-relative paths for one plugin. ``adapted`` may be None."""
    if not re.fullmatch(NAME, plugin) or (adapted is not None and not re.fullmatch(NAME, adapted)):
        raise ValueError("Invalid plugin or adapted skill name")
    root = f"plugins/{plugin}"
    paths = {"plugin": plugin, "adapted": adapted, "root": root, "skills": f"{root}/skills/", "lock": f"{root}/shared-skills.lock.json"}
    if adapted:
        paths["core"] = f"skills/{adapted}/SKILL.md"
        paths["output"] = f"{root}/skills/{adapted}/SKILL.md"
        # The original ditto plugin keeps its adapter at the repository root.
        paths["adapter"] = ADAPTER if (plugin, adapted) == (DEFAULT_PLUGIN, DEFAULT_ADAPTED) else f"adapters/{plugin}/{adapted}.md"
    return paths


def plugin_registry(source):
    """Map plugin name -> catalog/adapted skill. Old snapshots imply one ditto plugin."""
    config = file_at(source, REGISTRY)
    if not config.exists():
        return {DEFAULT_PLUGIN: {"catalog": "memory", "adapted_skill": DEFAULT_ADAPTED}}
    data = json.loads(config.read_text())
    if not isinstance(data, dict) or not data:
        raise ValueError("Invalid plugin registry")
    for name, entry in data.items():
        if not re.fullmatch(NAME, name) or not isinstance(entry, dict) or not isinstance(entry.get("catalog"), str):
            raise ValueError("Invalid plugin registry")
        adapted = entry.get("adapted_skill")
        if adapted is not None and (not isinstance(adapted, str) or not re.fullmatch(NAME, adapted)):
            raise ValueError("Invalid plugin registry")
        names = catalog_names(source, entry["catalog"])
        if adapted is not None and names is not None and adapted not in names:
            raise ValueError("Adapted skill must belong to the plugin catalog")
    return data


def catalog_names(source, catalog="memory"):
    """Select an explicit surface; old source snapshots retain their catalog."""
    config = file_at(source, "scripts/catalogs.json")
    if not config.exists():
        if catalog == "memory":
            return None
        raise ValueError("Unknown or invalid skill catalog")
    catalogs = json.loads(config.read_text())
    names = catalogs.get(catalog) if isinstance(catalogs, dict) else None
    if not isinstance(names, list) or not names or any(not isinstance(name, str) for name in names) or len(set(names)) != len(names):
        raise ValueError("Unknown or invalid skill catalog")
    for name in names:
        if not isinstance(name, str) or not re.fullmatch(NAME, name):
            raise ValueError("Invalid catalog skill name")
        if not file_at(source, f"skills/{name}/SKILL.md").is_file():
            raise ValueError("Catalog skill is missing")
    return set(names)


def additional_files(source, plugin=DEFAULT_PLUGIN, catalog="memory", adapted=DEFAULT_ADAPTED):
    """New public-text skills/references are discovered without new host forks."""
    paths = layout(plugin, adapted)
    result = {}
    skill_root = file_at(source, "skills")
    selected = catalog_names(source, catalog)
    core = file_at(source, paths["core"]) if adapted else None
    for item in sorted(skill_root.rglob("*")):
        if item.is_symlink():
            raise ValueError("Symlink in canonical skills")
        if not item.is_file() or item == core:
            continue
        relative = item.relative_to(Path(source).resolve())
        if selected is not None and relative.parts[1] not in selected:
            continue
        if len(relative.parts) < 3 or not re.fullmatch(r"[a-z0-9-]+", relative.parts[1]):
            raise ValueError("Unexpected skill layout")
        if item.suffix not in {".md", ".json", ".yaml", ".yml", ".txt"}:
            raise ValueError("Common distribution supports public text; executables/assets need an explicit adapter review")
        content = public_text(item.read_bytes())
        if item.name == "SKILL.md" and not re.match(rb"\A---\nname: " + relative.parts[1].encode() + rb"\ndescription: [^\n]+\n---\n", content):
            raise ValueError("Invalid additional skill frontmatter")
        result[f"{paths['root']}/" + relative.as_posix()] = content
    for relative in result:
        name = Path(relative).parts[3]
        if not file_at(source, f"skills/{name}/SKILL.md").is_file():
            raise ValueError("References require a skill entrypoint")
    return result


def bump_manifests(repo, host, plugin):
    files = [file_at(repo, f"plugins/{plugin}/{rel}") for rel in PLUGIN_MANIFESTS[host]]
    if not files[0].exists():
        raise ValueError("Missing primary host manifest")
    present = [(f, json.loads(f.read_text())) for f in files if f.exists()]
    if any("version" not in m for _, m in present):
        raise ValueError("Every host manifest in one plugin must carry a version before bumping")
    versions = {m["version"] for _, m in present}
    if len(versions) != 1:
        raise ValueError("Host manifests in one plugin must share a version before bumping")
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", versions.pop())
    if not match:
        raise ValueError("Automatic patch bump requires a stable three-part version")
    new = f"{match[1]}.{match[2]}.{int(match[3]) + 1}"
    for f, m in present:
        m["version"] = new
        f.write_text(json.dumps(m, indent=2) + "\n")
    return [f.relative_to(Path(repo).resolve()).as_posix() for f, _ in present]


def build(source, repo, host, bump_version=False, plugin=DEFAULT_PLUGIN, catalog="memory", adapted=DEFAULT_ADAPTED):
    paths = layout(plugin, adapted)
    sha = source_identity(source)
    generator = file_at(source, GENERATOR).read_bytes()
    extra = additional_files(source, plugin, catalog, adapted)
    extra_hashes = {relative: digest(value) for relative, value in extra.items()}
    outputs = []
    lock = {"schema_version": 1, "source_repository": SOURCE_REPOSITORY, "source_commit": sha, "host": host}
    if plugin != DEFAULT_PLUGIN or adapted != DEFAULT_ADAPTED:
        lock.update({"plugin": plugin, "adapted_skill": adapted})
    skill = None
    if adapted:
        core = public_text(file_at(source, paths["core"]).read_bytes())
        adapter = public_text(file_at(repo, paths["adapter"]).read_bytes())
        if not re.match(rb"\A---\nname: " + adapted.encode() + rb"\ndescription: [^\n]+\n---\n", core):
            raise ValueError("Invalid canonical skill frontmatter")
        skill = core + MARKER + adapter
        lock.update({"core_sha256": digest(core), "adapter_sha256": digest(adapter)})
        outputs.append((paths["output"], skill))
    lock.update({"generator_sha256": digest(generator)})
    if skill is not None:
        lock["skill_sha256"] = digest(skill)
    lock["files_sha256"] = extra_hashes
    lock_file = file_at(repo, paths["lock"])
    old = json.loads(lock_file.read_text()) if lock_file.exists() else {}
    # Do not churn release versions just because unrelated source docs moved.
    content_keys = ("core_sha256", "adapter_sha256", "generator_sha256", "files_sha256")
    if old and all(old.get(k) == lock.get(k) for k in content_keys) and old.get("host") == host:
        verify(repo, host, plugin=plugin)
        return False
    output_changed = skill is not None and (not file_at(repo, paths["output"]).exists() or file_at(repo, paths["output"]).read_bytes() != skill)
    if bump_version and (output_changed or skill is None and not old or old.get("files_sha256", {}) != extra_hashes):
        bump_manifests(repo, host, plugin)
    # A renamed or dropped adapted skill leaves its previous output behind;
    # old locks without the key used the default adapted skill.
    if old:
        stale = layout(plugin, old.get("adapted_skill", DEFAULT_ADAPTED)).get("output")
        if stale and stale != paths.get("output") and stale not in extra:
            file_at(repo, stale).unlink(missing_ok=True)
    for relative in old.get("files_sha256", {}):
        if relative not in extra:
            if not relative.startswith(paths["skills"]) or ".." in Path(relative).parts or relative == paths.get("output"):
                raise ValueError("Invalid previously generated path")
            file_at(repo, relative).unlink(missing_ok=True)
    for relative, content in [*outputs, (GENERATOR, generator), *extra.items(), (paths["lock"], (json.dumps(lock, indent=2) + "\n").encode())]:
        dest = file_at(repo, relative)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
    verify(repo, host, source, plugin=plugin)
    return True


def build_all(source, repo, host, bump_version=False):
    """Build every plugin in the source registry that the distribution hosts."""
    changed = {}
    for plugin, entry in plugin_registry(source).items():
        if host != "plugins" and plugin != DEFAULT_PLUGIN:
            continue  # single-host repositories carry only the original plugin
        if not file_at(repo, f"plugins/{plugin}/{PLUGIN_MANIFESTS[host][0]}").exists():
            raise ValueError(f"Distribution lacks the {plugin} plugin manifest; scaffold it before generating")
        changed[plugin] = build(source, repo, host, bump_version, plugin, entry["catalog"], entry.get("adapted_skill"))
    return changed


def verify(repo, host, source=None, plugin=DEFAULT_PLUGIN):
    lock = json.loads(file_at(repo, f"plugins/{plugin}/shared-skills.lock.json").read_text())
    if lock.get("schema_version") != 1 or lock.get("source_repository") != SOURCE_REPOSITORY or lock.get("host") != host:
        raise ValueError("Unexpected source or host provenance")
    if lock.get("plugin", DEFAULT_PLUGIN) != plugin:
        raise ValueError("Lock belongs to a different plugin")
    adapted = lock.get("adapted_skill", DEFAULT_ADAPTED) if "core_sha256" in lock or "adapted_skill" in lock else None
    paths = layout(plugin, adapted)
    if not re.fullmatch(r"[0-9a-f]{40}", lock.get("source_commit", "")):
        raise ValueError("Source must be an immutable Git commit")
    actual = {"generator_sha256": digest(file_at(repo, GENERATOR).read_bytes())}
    core = None
    if adapted:
        skill = file_at(repo, paths["output"]).read_bytes()
        if skill.count(MARKER) != 1:
            raise ValueError("Missing or repeated shared-core boundary")
        core, adapter = skill.split(MARKER)
        public_text(core)
        public_text(adapter)
        if adapter != file_at(repo, paths["adapter"]).read_bytes():
            raise ValueError("Generated host adapter drift")
        actual.update({"core_sha256": digest(core), "adapter_sha256": digest(adapter), "skill_sha256": digest(skill)})
    if any(lock.get(key) != value for key, value in actual.items()):
        raise ValueError("Generated skill or generator differs from recorded hashes")
    extra_hashes = lock.get("files_sha256", {})
    for relative, expected in extra_hashes.items():
        if not relative.startswith(paths["skills"]) or ".." in Path(relative).parts or relative == paths.get("output") or digest(file_at(repo, relative).read_bytes()) != expected:
            raise ValueError("Additional generated skill drift")
    installed = file_at(repo, paths["skills"].rstrip("/"))
    for item in installed.rglob("*"):
        if item.is_symlink() or (item.is_file() and item.relative_to(Path(repo).resolve()).as_posix() not in {paths.get("output"), *extra_hashes}):
            raise ValueError("Untracked generated skill file or symlink")
    if source is not None:
        entry = plugin_registry(source).get(plugin)
        if entry is None or source_identity(source) != lock["source_commit"] or (adapted and file_at(source, paths["core"]).read_bytes() != core) or file_at(source, GENERATOR).read_bytes() != file_at(repo, GENERATOR).read_bytes() or {p: digest(v) for p, v in additional_files(source, plugin, entry["catalog"], adapted).items()} != extra_hashes:
            raise ValueError("Release does not match canonical source")
    return lock


def locked_plugins(repo):
    """Plugins in a distribution that carry generated shared skills."""
    names = sorted(p.parent.name for p in file_at(repo, "plugins").glob("*/shared-skills.lock.json"))
    if not names:
        raise ValueError("No generated plugin locks found")
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["build", "verify"])
    parser.add_argument("--host", choices=MANIFESTS, required=True)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path)
    parser.add_argument("--plugin", help="limit verify to one plugin (default: every locked plugin)")
    parser.add_argument("--bump-version", action="store_true")
    args = parser.parse_args()
    if args.command == "build":
        if args.source is None:
            parser.error("build requires --source")
        for plugin, changed in build_all(args.source, args.repo, args.host, args.bump_version).items():
            print(f"{args.host}/{plugin}: generated={changed}; shared skills verified")
    else:
        for plugin in [args.plugin] if args.plugin else locked_plugins(args.repo):
            lock = verify(args.repo, args.host, args.source, plugin=plugin)
            count = ("core_sha256" in lock) + sum(p.endswith('/SKILL.md') for p in lock.get('files_sha256', {}))
            print(f"{args.host}/{plugin}: {count} skill(s) verified; source={lock['source_commit']}")


if __name__ == "__main__":
    main()
