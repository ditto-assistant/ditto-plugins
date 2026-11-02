# Local ChatGPT and Codex testing

> Moved from the retired `ditto-assistant/ditto-openai-plugins` repository (DITTO-1674). ChatGPT and Codex now ship from `plugins/ditto` here: the portable `.openai-plugin/plugin.json` carries the OpenAI listing, `mcp.json` the hosted server, and `python3 scripts/validate_package.py --archive <zip>` builds the directory upload. The plugin shares one version with every other host (0.4.0 at the move).

This repository's `.agents/plugins/marketplace.json` exposes the portable package
for local testing. It is separate from store submission/publication.

Add the reviewed main branch with:

```sh
codex plugin marketplace add ditto-assistant/ditto-plugins --ref main
codex plugin list --marketplace ditto-plugins --available --json
```

Use the ChatGPT desktop Plugins Directory, choose the **ditto-plugins** marketplace, and
install Ditto. Where the installed CLI supports it, `codex plugin add
ditto@ditto-plugins --json` installs the local plugin. Refresh/restart the
intended host when required. Verify its installed version and discovery of the
20 bundled skills in the intended chat. CLI/package success
alone does not prove the ChatGPT UI refreshed or that MCP authentication works.
Complete sign-in through the host, never paste credentials in chat. Reuse the
existing Ditto connection when available; no store listing is submitted here.

Run a bounded handoff exercise only on a selected test chat. Verify private
save/full readback, then the exact host's supported archive action. Codex desktop
may expose `set_thread_archived`; prefer its documented implicit-current-chat
form when available. Eligible managed worktrees can use `archive_worktree` after
ownership, authorization and file recovery checks; preserve needed ignored files
separately and verify the snapshot receipt. These host tools are not Ditto MCP
tools and may be absent in ChatGPT or browser-only sessions. Do not invent APIs
or edit host databases. No archive support means saved memory plus manual closeout.

Browser-only ChatGPT cannot measure or delete local files without an authorized
local filesystem/computer tool. Disk pressure is assessed when capable; exact
owned cleanup remains separately authorized. A summary is not a code/file backup.
Bulk requests run serially with per-chat receipts and idempotent reconciliation.

Official guidance: [package and local marketplace setup](https://developers.openai.com/plugins/build/plugins)
and [complete-plugin testing](https://developers.openai.com/plugins/deploy/connect-chatgpt).
