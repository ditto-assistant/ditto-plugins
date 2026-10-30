# Contributing

This repository is a multi-plugin, multi-host marketplace. Each plugin lives in
`plugins/<name>/` with one shared `skills/` folder and a native manifest for each
host. Every root marketplace lists the same plugins, and
`scripts/validate_package.py` enforces that.

## Add a plugin

1. **Skills source.** In `ditto-assistant/ditto-skills`, add the skills and a
   catalog in `scripts/catalogs.json`. Register the plugin in `scripts/plugins.json`,
   e.g. `"ditto-partner": {"catalog": "partners"}`. Add `"adapted_skill"` only if one
   skill needs this repository's host-connection adapter appended to it.
2. **Scaffold `plugins/<name>/`** here by copying `plugins/ditto/` without
   `skills/` and `shared-skills.lock.json`. Then:
   - set `name` to `<name>` in all seven host manifests (`.claude-plugin`,
     `.cursor-plugin`, `.grok-plugin`, `.codex-plugin`, `.github/plugin`,
     `.antigravity-plugin`, `.kimi-plugin`), and give them one shared `version`.
   - write host-tailored descriptions, keywords and display names. For example,
     "Sign in through Cursor" goes in the Cursor manifest, and Grok keywords must be
     brand-scoped because the Grok catalog uses them for its call-to-action.
   - put assets in `assets/` and reference them with relative `./assets/...` paths.
   - rename the MCP server key to `<name>` in `.mcp.json`, `mcp.json`,
     `mcp_config.json` and the inline Copilot and Kimi entries.
3. **Allow its endpoint.** Add `<name>: <https MCP URL>` to `HOSTED_MCP` in
   `scripts/validate_package.py`. Only hosted HTTP servers are allowed: no
   commands, headers, env or credentials.
4. **List it in every root marketplace**: `.claude-plugin`, `.cursor-plugin`,
   `.grok-plugin`, `.agents/plugins` and `.github/plugin`. Use the source
   `./plugins/<name>`, and set category and description in each host's own vocabulary.
5. **Generate skills** from a clean ditto-skills checkout:
   `python3 scripts/shared_skills.py build --host plugins --source <clone> --repo . --bump-version`.
   After that, the ditto-skills distribution workflow proposes updates as PRs.
6. Add a row to the README plugin table. Then run the validation commands in the README.

## Host-specific content

All hosts load the same `skills/` folder from a plugin directory. Claude and Grok
always scan `skills/`, so separate skill trees per host are not possible within
one plugin. Put host differences in:

- **manifests**: display name, logo, category, prompts, brand color
- **MCP config files**: each host's transport field names
- **host-labelled sections** of an adapter such as `adapters/ditto-memory.md`

Edit an adapter here, then regenerate. Common skill text is edited only in ditto-skills.

## Releases

Pushes to `main` update every marketplace that tracks this repository, and may
trigger Claude directory scans. Work on a branch and open a PR. Merge only with
authorization. See [RELEASING.md](RELEASING.md).
