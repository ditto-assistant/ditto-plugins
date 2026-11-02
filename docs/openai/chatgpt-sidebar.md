# ChatGPT sidebar entrypoint

> Moved from the retired `ditto-assistant/ditto-openai-plugins` repository (DITTO-1674). ChatGPT and Codex now ship from `plugins/ditto` here: the portable `.openai-plugin/plugin.json` carries the OpenAI listing, `mcp.json` the hosted server, and `python3 scripts/validate_package.py --archive <zip>` builds the directory upload. The plugin shares one version with every other host (0.4.0 at the move).

The existing `ditto` plugin connects directly to `https://api.heyditto.ai/mcp` through `plugins/ditto/mcp.json`. The backend owns the UI resource and sidebar registration. Do not add a second plugin, a `homepageTool` manifest key, an app binding, or a separate frontend.

Under DITTO-758, the backend registers the existing read-only `list_memories` tool with `_meta.ui.resourceUri` and `_meta["openai/ui"].entrypoints: [{ "type": "global" }]`. ChatGPT launches it with `{}`. The same memory dashboard accepts fullscreen and inline display, renders the launch result, and retains search, recent-memory and explicit full-inspection actions. Initial content covers externally-saved memories, not every native Ditto chat. OAuth, graph permissions and credential tool allowlists still apply. Credentials that cannot call `list_memories` do not gain a sidebar route around that restriction.

The sidebar declaration is server metadata; the package identity, connection configuration and listing URLs remain unchanged. An external website/homepage URL does not register a sidebar app. The server must be deployed, and the installed host connection must refresh or rescan its tools/resources, before the entry can appear. Published connector updates and public-directory publication are separate from merging source.

## Host acceptance

In a supported ChatGPT desktop installation with this package connected:

1. Refresh the connection's MCP metadata after the backend release. Confirm exactly one global entrypoint on `list_memories` and a readable linked UI resource.
2. Open Ditto from the global navigation and pin it if desired. Confirm the existing Ditto identity and a fullscreen dashboard showing the authorized initial recent-memory page, or an accurate empty/error state.
3. Search for known saved context and explicitly inspect one memory. Confirm the accepted workspace is preserved and no additional full-memory read happens just from opening an outline.
4. Confirm normal memory tools still return useful text in a host without MCP Apps support.

Local package validation checks the upload source and ZIP. Backend wire and reference-host browser tests check metadata, empty-argument launch, fallback and fullscreen rendering. Neither establishes the installed ChatGPT sidebar, OAuth sign-in, directory eligibility or publication. Record actual host evidence separately under DITTO-426; keep DITTO-758 in verification until that evidence exists. Claude plugin changes remain outside this ChatGPT slice.

Reference: [OpenAI sidebar apps](https://developers.openai.com/plugins/build/extensions#sidebar-apps).
