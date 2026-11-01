# Ditto

Connect your AI host to your Ditto memory through the hosted MCP server at
https://api.heyditto.ai/mcp. Sign in through the host's own connection controls;
never paste API keys into chat. The package includes no CLI helper or lifecycle hooks.

This one folder is a native plugin for each supported host:

| Host | Manifest | MCP config | Install |
| --- | --- | --- | --- |
| Claude Code, Chat, Cowork | `.claude-plugin/plugin.json` | `.mcp.json` | `/plugin marketplace add ditto-assistant/ditto-plugins`, `/plugin install ditto@ditto-claude-plugins` |
| Cursor | `.cursor-plugin/plugin.json` | `.mcp.json` | Customize → Marketplace → Ditto |
| Grok Build | `.grok-plugin/plugin.json` | `.mcp.json` | `grok plugin install ditto --trust` after `grok plugin marketplace add ditto-assistant/ditto-plugins` |
| Codex | `.codex-plugin/plugin.json` | `mcp.json` | `codex plugin marketplace add ditto-assistant/ditto-plugins`, then `/plugins` |
| GitHub Copilot, VS Code | `.github/plugin/plugin.json` | inline | `copilot plugin install ditto@ditto-plugins` |
| Antigravity | `.antigravity-plugin/plugin.json` | `mcp_config.json` | `/plugin install ./plugins/ditto` from a clone |
| Kimi Code | `.kimi-plugin/plugin.json` | inline | local install from a clone |

Claude desktop Chat/Cowork and Claude Code have separate plugin installations; in
Chat and Cowork, add the `ditto-assistant/ditto-plugins` repository under
Customize → Plugins → Add marketplace. See the [repository README](../../README.md)
for each host's full steps.

Use `/ditto-memory` to search memories, fetch supporting content, and save or
update useful information when authorized. Live MCP schemas determine available
tools and permissions. If the connection is unavailable, reconnect in the host
rather than substituting shell commands or creating a new agent account.

Use `/curate-music` to curate a playlist for your preferred music service from
verified Ditto context and an accessible saved music library. Service connectors
come first, browser/computer controls next, and web search last for recordings,
official links and an ordered plan. Saving playlists or changing playback requires
separate music capabilities; confirm the actual result before claiming success.

Try: "Curate a playlist on my preferred music service using my Ditto memories for
a relaxed evening, with a few discoveries."

Use `/handoff` for verified private
continuation notes and supported host archival, including explicitly selected
bulk closeout. Disk assessment requires local tools; cleanup requires exact
authority and verified code/file recovery. A memory summary is not a file backup.
If this host cannot archive, the skill saves the handoff and explains the manual
closeout step. Exiting a CLI session is not an archive operation.

The plugin respects your current instructions, private capture preferences,
source authorship and actual tool grants. The plugin does not automatically save
transcripts or inject context at every prompt. Native chat listing/sending and
music-account access are not supplied by this package. UI support depends on the
actual host. Installation alone does not prove authenticated tool execution.

Upgrading from 0.2.x removes the old plugin's CLI hooks and commands. Previously
installed CLI software, credentials, agent accounts and saved memories remain;
manage those separately if no longer needed. Reload or restart running sessions
to pick up the new plugin components.

Support: support@heyditto.ai. [Privacy](https://heyditto.ai/privacy) ·
[Terms](https://heyditto.ai/terms). Music skill adapted from Omar Barazanji's
[heyditto-stack PR #115](https://github.com/ditto-assistant/heyditto-stack/pull/115).
