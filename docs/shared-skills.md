# Shared skill releases

The common memory and music-curation workflows come from the private `ditto-assistant/ditto-skills` source repo. Edit common behavior there. Edit this repository's `adapters/ditto-memory.md` for host-specific guidance (one labelled section per host, because every host reads the same generated skill); MCP configuration and host-managed sign-in guidance remain owned here. This MCP-only package ships no CLI helpers, lifecycle hooks or shell commands.

The generated SKILL.md, offline verifier and shared-skills.lock.json are materialized files, not symlinks. The lock records the immutable source revision and content hashes. Run `python3 scripts/shared_skills.py verify --host plugins --repo .` without private repo access. A maintainer with a clean source clone can run its generator with `build --source <clone> --repo . --host plugins --bump-version`.

Source main changes open distribution PRs through the source workflow. They do not merge, submit to a store or change hosted MCP behavior. A patch version is raised in every host manifest of the plugin when skill text changes. Each source SHA has one proposal per host; a rejected/edited proposal requires maintainer attention rather than an automatic overwrite.

Offline hashes detect drift, not publisher identity. Verify the source commit and review host behavior before merging a generated PR. Directory approval and installed-host behavior remain separate from these checks.
