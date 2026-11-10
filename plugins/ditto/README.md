# Ditto

Connect your AI host to your Ditto memory through the hosted MCP server at
https://api.heyditto.ai/mcp. Sign in through the host's own connection controls;
never paste API keys into chat. The package includes no CLI helper. In Claude Code,
small local [lifecycle hooks](#lifecycle-hooks) remind the agent to use Ditto memory.

This one folder is a native plugin for each supported host:

| Host | Manifest | MCP config | Install |
| --- | --- | --- | --- |
| Claude Code, Chat, Cowork | `.claude-plugin/plugin.json` | `.mcp.json` | `/plugin marketplace add ditto-assistant/ditto-plugins`, `/plugin install ditto@ditto-claude-plugins` |
| Cursor | `.cursor-plugin/plugin.json` | `.mcp.json` | Customize → Marketplace → Ditto |
| Grok Build | `.grok-plugin/plugin.json` | `.mcp.json` | `grok plugin install ditto --trust` after `grok plugin marketplace add ditto-assistant/ditto-plugins` |
| Codex | `.codex-plugin/plugin.json` | `mcp.json` | `codex plugin marketplace add ditto-assistant/ditto-plugins`, then `/plugins` |
| GitHub Copilot, VS Code | `.github/plugin/plugin.json` | inline | `copilot plugin install ditto@ditto-plugins` |
| Antigravity | `.antigravity-plugin/plugin.json` | `mcp_config.json` | `agy plugin install https://github.com/ditto-assistant/ditto-plugins` |
| Kimi Code | `.kimi-plugin/plugin.json` | inline | `/plugins install https://github.com/ditto-assistant/ditto-plugins` |
| ChatGPT | `.openai-plugin/plugin.json` | `mcp.json` | ChatGPT directory |

Claude desktop Chat/Cowork and Claude Code have separate plugin installations; in
Chat and Cowork, add the `ditto-assistant/ditto-plugins` repository under
Customize → Plugins → Add marketplace. See the [repository README](../../README.md)
for each host's full steps.

## Skills

Twenty skills put your Ditto memory to work. Each one recalls what Ditto knows
first, saves only what you approve, and sets up a Ditto workflow, agent or shared
space only when you agree to that specific one.

- **Memory:** `ditto-memory`, `handoff`, `tidy-memory` (fix duplicate and stale
  memories), `decision-log` (decisions with rationale, shared with your team).
- **Business:** `prep-meeting`, `weekly-review`, `research-brief`, `write-spec`,
  `launch-post`.
- **Engineering:** `grill-me` (stress-test a plan), `diagnose-bug`, `tdd`,
  `code-review`, `verify-done`.
- **Life:** `daily-brief`, `learn-anything`, `plan-trip`, `plan-meals`,
  `gift-ideas`, `curate-music`.

Try: "Prepare me for my meeting with the Cedar team", "Grill me on this plan",
"Run my weekly review", or "Plan meals for this week around what my family likes."

Use `/ditto-memory` to search memories, fetch supporting content, and save or
update useful information when authorized. Live MCP schemas determine available
tools and permissions. If the connection is unavailable, reconnect in the host
rather than substituting shell commands or creating a new agent account.

Use `/curate-music` to curate a playlist for your preferred music service from
verified Ditto context and an accessible saved music library. Service connectors
come first, browser/computer controls next, and web search last for recordings,
official links and an ordered plan. Saving playlists or changing playback requires
separate music capabilities; confirm the actual result before claiming success.

## Lifecycle hooks

Claude Code runs `hooks/claude-hooks.json`. Each handler calls `hooks/ditto-hook.sh`
with a 5-second timeout and fails open. The script prints fixed reminders and
makes no network calls; Ditto reads and writes still go through the agent's MCP
connection.

- **Session start:** search Ditto with `ditto-memory` before work that depends on
  the user's history, people, projects or past decisions.
- **Compaction:** the summary keeps Ditto memory IDs and marks outcomes not yet
  saved. After compaction the agent reuses those IDs and saves what is still
  unsaved, if capture is authorized.
- **Stop:** once per session, after a file edit or ten tool calls with no Ditto save,
  the agent saves one concise outcome note if you authorized capture, and otherwise
  offers to. This costs one short extra turn.

`DITTO_HOOKS=0` turns them all off; `DITTO_HOOKS_STOP=0` turns off only the Stop
check. Other hosts get no hooks yet. See
[docs/hooks.md](../../docs/hooks.md) for the rationale and each host's support.

## Other services and host capabilities

The Ditto MCP server supplies memory access. Skills may also use separately
connected services or host tools when available and authorized:

- Music accounts: Spotify, Apple Music, YouTube Music, Tidal, Deezer, Amazon
  Music, SoundCloud, or another service the user selects. The music skill may
  read a saved library and, with separate capability, create playlists or control
  playback.
- Web search for current public facts, sources, travel and meal planning, and
  music links; browser or computer control for music sites and other user
  requested UI work.
- Connected calendars, task lists, and user named research sources for briefs,
  meetings, and daily planning. Connected shopping, booking, publishing, and
  messaging services are used only for the corresponding user requested action.
- Host repository, test runner, filesystem, and chat archive controls for
  engineering and handoff skills, subject to the host's grants and user approval.

These are host capabilities, not servers or credentials bundled with this plugin.
Availability depends on the host and the user's connections.

Try: "Curate a playlist on my preferred music service using my Ditto memories for
a relaxed evening, with a few discoveries."

Use `/handoff` for verified private
continuation notes and supported host archival, including explicitly selected
bulk closeout. In a chat app it only writes the note, saves it, reads it back
and closes the chat. Coding agents with a local workspace also make code
recoverable and, with exact authority, clean up their own files; those steps
live in the skill's `references/coding-agent.md`. A memory summary is not a file
backup. If this host cannot archive, the skill saves the handoff and explains the
manual closeout step. Exiting a CLI session is not an archive operation.

Every skill works in a chat app. Steps that need a shell, such as git, test
runners, disk checks and deploy probes, sit in a skill's
`references/coding-agent.md`, which chat hosts skip.

The plugin respects your current instructions, private capture preferences,
source authorship and actual tool grants. The plugin does not automatically save
transcripts or inject context at every prompt; its hooks only remind the agent. Native chat listing/sending and
music-account access are not supplied by this package. UI support depends on the
actual host. Installation alone does not prove authenticated tool execution.

Upgrading from 0.2.x removes the old plugin's CLI hooks and commands; today's
hooks are local reminders with no CLI. Previously
installed CLI software, credentials, agent accounts and saved memories remain;
manage those separately if no longer needed. Reload or restart running sessions
to pick up the new plugin components.

Support: support@heyditto.ai. [Privacy](https://heyditto.ai/privacy) ·
[Terms](https://heyditto.ai/terms). Several engineering and learning skills are
original adaptations of ideas from [mattpocock/skills](https://github.com/mattpocock/skills)
(MIT). Music skill adapted from Omar Barazanji's
[heyditto-stack PR #115](https://github.com/ditto-assistant/heyditto-stack/pull/115).
