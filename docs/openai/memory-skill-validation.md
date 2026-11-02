# Memory skill review and package validation

> Moved from the retired `ditto-assistant/ditto-openai-plugins` repository (DITTO-1674). ChatGPT and Codex now ship from `plugins/ditto` here: the portable `.openai-plugin/plugin.json` carries the OpenAI listing, `mcp.json` the hosted server, and `python3 scripts/validate_package.py --archive <zip>` builds the directory upload. The plugin shares one version with every other host (0.4.0 at the move).

October 12, 2026. Prepared on the existing PR 2 branch for review under DITTO-764.

## Content change

The existing memory skill now recalls relevant supporting bodies before using user history, captures durable context only within the user's authorized private capture workflow, updates matching records rather than duplicating them, preserves source provenance and status distinctions, and checks write receipts. It retains scoped access and external action boundaries. Personal identity, task records, private memory identifiers, contacts, local host paths and global personal policy were not copied into the skill or public upload.

The existing plugin identity, version 0.1.0, hosted MCP endpoint, OAuth ownership, icon, review cases and country targeting were preserved. Capture instructions do not install hooks or guarantee automatic loading in every host. UI claims were not expanded.

## Reproduce the local checks

Use Python 3.9 or newer. From the repository root run `python3 scripts/validate_package.py`. Add `--archive /path/outside/plugin/ditto.zip` to create and verify a ZIP with one ditto directory. The validator compares archived bytes and inventory with the validated source and excludes repository dependencies, symlinks, environment files, app bindings and bundled hooks.

The script is an implementation of local package checks, not a full target portal validator or proof of policy compliance. Its sensitive-content patterns catch common local paths, memory UUIDs and inline Ditto keys; they do not replace manual privacy review.

## Verified checks

The generic skill passed the Skill Creator frontmatter validator. PyYAML used by that check was installed in a temporary validation directory and is not a plugin dependency.

The package check passed against all five source files. The archive was generated and its contents matched source bytes. Icons retain the existing 512 by 512 PNG. Listing subtitle and starter prompts fit the documented limits; five positive and three negative review cases remain present.

Separate temporary fixtures were rejected for app binding files, an icon path escaping the package, inline authorization headers on an otherwise valid MCP configuration, private host paths, a symlink, and an archive output inside the plugin directory. Whitespace checks passed. These are package checks, not executions of the eight MCP review cases.

## Pending evidence and review boundaries

The eight MCP cases remain NOT RUN in the intended submitted host. Authenticated host testing and a real recorded walkthrough still require sign-in and a dedicated populated test account. The private Ditto connector used for work memory is not proof that this package is installed or authenticated in ChatGPT or Codex. Reviewer credentials belong only in secure portal fields.

Payment location, publisher verification, current policy coverage and the intersection of Ditto's country policy with host-supported markets remain unresolved. Retain DITTO-423/758 for UI and Home, DITTO-424/425 for host release, DITTO-426 for cross-host QA and DITTO-427 for setup/adoption. Any larger UI or cross-repository implementation scope needs the user's review. The existing Claude source remains read only for this account and needs its maintainer.

No merge, production deployment, account change, directory submission or publication was performed. Technical review remains with the existing PR and release coordination.

## Technical review, October 14, 2026

Peyton's review reproduced the five-file package check, byte-verified ZIP and all six rejected fixtures above against review commit `6bbb5f9a4e3fa362eeaaaf990138b7469c7b6c49`. No blocking skill or validator issue was found. The ChatGPT sidebar implementation reuses the backend dashboard and existing `ditto` identity; see [the contract and host acceptance steps](chatgpt-sidebar.md). Actual installed-host cases and the listed submission dependencies remain unverified. Review and source merge do not establish deployment, sidebar discovery or publication.
