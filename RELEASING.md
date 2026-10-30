# Releasing

The 0.3.1 directory preparation release adds explicit listing metadata and the
unchanged sculptural-D app icon from brand-kit tag `v2026.09.10`
(`kit/png/ditto-app-icon-light-512.png`, SHA-256
`08b3a41e1c0987fb585260bd85f3c02913494a490a0a732d81d7c257c61845c3`).
MCP configuration and bundled skill bytes match the tested 0.3.0 release. Directory
validation reads the exact submitted commit separately from local validation.

The release contains hosted MCP connection metadata and shared skills. It does
not distribute or refresh a CLI, run hooks or provision agent accounts.

1. Change host manifests, MCP configuration or the host adapter here. Change common skills
   in `ditto-assistant/ditto-skills`; regenerate using its clean committed source.
2. Bump every host manifest in `plugins/<name>/` to the same version for a host change
   (the validator rejects diverged versions). The shared-skill
   generator automatically patch-bumps changed skill content; avoid a second bump.
3. Run the offline verifier, `python3 -m unittest discover -s tests -v`,
   `python3 scripts/validate_package.py`, `claude plugin validate ./plugins/ditto`, and
   `grok plugin validate ./plugins/ditto` where those CLIs are available.
4. Open a PR and inspect current-head CI and Ditto Review. Merge only when authorized.
   Every host marketplace tracks main, so merging updates the plugin on all hosts.
5. Refresh the marketplace and update Ditto in the actual host. Verify the installed
   version, two skills and Ditto MCP connector. Authenticate through the host flow
   and verify tools separately before claiming live memory behavior.

Claude Code users can run `/plugin marketplace update ditto-claude-plugins` then
`/reload-plugins`. Desktop Chat/Cowork users select Chat and Cowork, then use
Customize → Plugins. Verify each surface separately: Code's local marketplace
installation does not install the Chat/Cowork plugin. Confirm both bundled skills
in a new Chat's `/` menu and the plugin's Connected MCP connector. Running sessions may
need a restart. Do not clear global plugin caches or delete unrelated credentials.

The 0.3.0 migration replaces the former 0.2.x CLI implementation. Old CLI commands
and lifecycle hooks are absent from the new bundle. It does not remove prior local
CLI installations, credentials, agent accounts or saved memories. Host-managed
OAuth replaces plugin-managed CLI keys; authentication may need reconnecting.

Merging or installing a package is not a store submission. Directory submission,
reviewer access, demos and functional host tests are separate release gates.
