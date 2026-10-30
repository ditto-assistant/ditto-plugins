## Host connection

Use the hosted Ditto MCP server at https://api.heyditto.ai/mcp, declared by this plugin's MCP configuration. Sign-in is host-managed OAuth: complete it through the current host's connection controls, never by pasting API keys into chat. Find your host below and follow only that section; availability and UI depend on the actual host and version.

- **Claude** (Code, desktop Chat and Cowork): the server comes from `.mcp.json`. In Claude Code, inspect and authenticate it in `/mcp`; in Chat or Cowork, use the plugin's connector controls. Skills appear in the `/` menu under Ditto.
- **Cursor**: the server comes from `.mcp.json` and appears under Customize → MCP servers; sign in there when Cursor prompts. Skills load under Agent Decides and can be invoked with `/skill-name` in chat.
- **Grok** (Grok Build CLI and Grok apps): the plugin's `.mcp.json` server attaches once the plugin is trusted. Check it in `/mcps` and sign in when prompted. Skills appear as `/ditto:<skill>`.
- **Codex and ChatGPT**: the server comes from `mcp.json`. Authenticate through the plugin's install or connection prompt; in the Codex CLI, `/mcp` shows its status.
- **GitHub Copilot and VS Code**: the server is declared in the plugin manifest. Start and sign in from the MCP servers view or the Copilot CLI's `/mcp`.
- **Antigravity**: the server comes from `mcp_config.json`. Sign in from the MCP servers panel when prompted.
- **Other hosts**: use whatever MCP connection UI the host provides for the plugin's declared server.

Discover the connected server's live tools and resources, including `memory://capabilities` when exposed. Use its MCP tools for search, full-content fetch and authorized saves or updates; do not invent tool names or assume every host exposes every capability. If the server is missing or authentication has expired, explain the gap and ask the user to connect or reconnect through the host. Never request API keys in chat or fall back to shell memory commands.

This package does not install the Ditto CLI, create agent accounts, run lifecycle hooks, inject context on every prompt, or automatically save transcripts. Follow the shared workflow for deliberate recall and authorized private capture. Music-service controls are separate capabilities; the Ditto MCP connection supplies memory context, not music-account access.
