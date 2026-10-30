# Ditto plugins

Ditto's official plugin marketplace for AI coding and chat hosts. One repository,
one shared set of skills, and a native manifest for each host. Every plugin connects
to the hosted Ditto MCP server at https://api.heyditto.ai/mcp for memory search,
supporting context, and authorized private saves or updates. Sign-in is the host's
own OAuth flow: no API keys, npm helpers, CLI bootstrap or lifecycle hooks.

> This repository was renamed from `ditto-assistant/ditto-claude-plugins`. GitHub
> redirects the old URL, and the Claude marketplace keeps the name
> `ditto-claude-plugins` so existing Claude installs keep updating.

## Plugins

| Plugin | What it does | Skills |
| --- | --- | --- |
| [`ditto`](plugins/ditto/) | Ditto memory over hosted MCP | `ditto-memory`, `handoff`, `curate-music` |

## Install

| Host | Marketplace file | Install |
| --- | --- | --- |
| Claude Code | `.claude-plugin/marketplace.json` | `/plugin marketplace add ditto-assistant/ditto-plugins` then `/plugin install ditto@ditto-claude-plugins` |
| Claude desktop (Chat, Cowork) | `.claude-plugin/marketplace.json` | Customize → Plugins → Add → Add marketplace → Add from a repository → `ditto-assistant/ditto-plugins` |
| Cursor | `.cursor-plugin/marketplace.json` | Cursor Marketplace once listed; teams: Dashboard → Plugins & MCPs → Import from Repo |
| Grok Build | `.grok-plugin/marketplace.json` | `grok plugin marketplace add ditto-assistant/ditto-plugins` then `grok plugin install ditto --trust` |
| Codex | `.agents/plugins/marketplace.json` | `codex plugin marketplace add ditto-assistant/ditto-plugins`, then install Ditto from `/plugins` |
| GitHub Copilot CLI / VS Code | `.github/plugin/marketplace.json` | `copilot plugin marketplace add ditto-assistant/ditto-plugins` then `copilot plugin install ditto@ditto-plugins` |
| Antigravity | `plugins/ditto/.antigravity-plugin/` | Clone, then `/plugin install ./plugins/ditto` |
| Kimi Code | `plugins/ditto/.kimi-plugin/` | Install from a local clone of `plugins/ditto` |

### Claude

For **Claude Chat or Cowork**, select **Chat and Cowork** in Claude desktop first.
Open Customize → Plugins → Add → Add marketplace → Add from a repository, select
`ditto-assistant/ditto-plugins`, and Sync. Add Ditto from that marketplace.
Under Yours, verify Ditto is enabled, Skills lists `curate-music`, `ditto-memory`
and `handoff`, and Connectors shows Ditto Connected. In a new Chat, type `/` and
verify all three skills appear under Ditto before sending your request.

Claude Code has a separate plugin installation. A plugin visible in Code does not
by itself mean it is installed in Chat. For **Claude Code**:

```text
/plugin marketplace add ditto-assistant/ditto-plugins
/plugin install ditto@ditto-claude-plugins
```

Inspect and authenticate the plugin-provided Ditto server in `/mcp`. To update:

```text
/plugin marketplace update ditto-claude-plugins
/plugin update ditto@ditto-claude-plugins
/reload-plugins
```

### Cursor

Open **Customize**, find **Ditto** in the Cursor Marketplace, and install it for
your user or a project. Teams can import this repository as a team marketplace
(Dashboard → Plugins & MCPs → Add Marketplace → Import from Repo) and turn on
Auto Refresh. To test locally, copy `plugins/ditto` to
`~/.cursor/plugins/local/ditto` and run **Developer: Reload Window**. Sign in to
Ditto under Customize → MCP servers. Skills load under Agent Decides and can be
invoked with `/ditto-memory`, `/handoff` or `/curate-music`.

### Grok

```sh
grok plugin marketplace add ditto-assistant/ditto-plugins
grok plugin install ditto --trust
```

Or open `/marketplace` in the Grok TUI. Plugins need trust to attach their MCP
server; check Ditto in `/mcps` and sign in when prompted. Skills appear as
`/ditto:ditto-memory`, `/ditto:handoff` and `/ditto:curate-music`.

### Codex

```sh
codex plugin marketplace add ditto-assistant/ditto-plugins
```

Install Ditto from `/plugins`, then complete the sign-in prompt. `/mcp` shows the
connection. The ChatGPT directory listing is published separately.

### GitHub Copilot and VS Code

```sh
copilot plugin marketplace add ditto-assistant/ditto-plugins
copilot plugin install ditto@ditto-plugins
```

In VS Code, add the marketplace repository from the agent plugins view. Start and
sign in to the Ditto server from the MCP servers view.

### Antigravity and Kimi Code

Clone this repository and install `plugins/ditto` as a local plugin
(`/plugin install ./plugins/ditto` in Antigravity). Antigravity reads
`mcp_config.json`; Kimi reads the server from `.kimi-plugin/plugin.json`.

The bundled skills are the verified loading path. The hosted MCP server also
offers the canonical skill files through `skills/list`, `skills/get` and
`resources/read` for compatible importers; keep the bundle installed. See the
[host compatibility check](docs/host-compatibility.md).

## Shared skills

- `/handoff`: save continuation context to private Ditto memory and compare full
  readback before archiving the current chat or an explicitly selected bulk set.
  Assess disk pressure and recoverability of owned workspaces/build artifacts;
  cleanup requires exact authorization. See [host limits](docs/handoff.md).
- `/ditto-memory`: recall evidence from saved memories and save or update useful
  information within the user's authorized private memory workflow.
- `/curate-music`: curate an ordered selection for the user's chosen music service
  using verified Ditto context and an accessible saved library. Creation and
  playback require separate music capabilities; Ditto MCP does not provide music APIs.

Skills are generated from the private `ditto-assistant/ditto-skills` source. Each
host reads the same `skills/` folder; host-specific connection guidance lives in
the host-labelled sections of [`adapters/ditto-memory.md`](adapters/ditto-memory.md).

## Layout

```text
.claude-plugin/marketplace.json        # Claude (name kept: ditto-claude-plugins)
.cursor-plugin/marketplace.json        # Cursor
.grok-plugin/marketplace.json          # Grok Build
.agents/plugins/marketplace.json       # Codex
.github/plugin/marketplace.json        # GitHub Copilot / VS Code
adapters/ditto-memory.md               # per-host connection guidance (source for the generated skill)
plugins/<name>/
  .claude-plugin/plugin.json  .cursor-plugin/plugin.json  .grok-plugin/plugin.json
  .codex-plugin/plugin.json   .github/plugin/plugin.json  .antigravity-plugin/plugin.json
  .kimi-plugin/plugin.json
  .mcp.json        # Claude, Cursor, Grok (type http)
  mcp.json         # Codex (streamable-http)
  mcp_config.json  # Antigravity (serverUrl)
  assets/          # icon.png, logo.svg
  skills/          # generated shared skills
  shared-skills.lock.json
```

To add a plugin, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Validate

```sh
python3 scripts/shared_skills.py verify --host plugins --repo .
python3 -m unittest discover -s tests -v
python3 scripts/validate_package.py
claude plugin validate ./plugins/ditto
grok plugin validate ./plugins/ditto
```

Source, package validation, installed plugin, authenticated MCP and actual tool
execution are separate verification steps. Nothing is submitted to a store by
this repository's validation or distribution pipeline. Maintainers: see
[RELEASING.md](RELEASING.md) and [shared skills](docs/shared-skills.md).

Support: support@heyditto.ai · [Privacy](https://heyditto.ai/privacy) ·
[Terms](https://heyditto.ai/terms). MIT — see [LICENSE](LICENSE).
