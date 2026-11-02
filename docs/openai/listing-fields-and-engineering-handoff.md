# Ditto plugin listing fields and engineering handoff

> Moved from the retired `ditto-assistant/ditto-openai-plugins` repository (DITTO-1674). ChatGPT and Codex now ship from `plugins/ditto` here: the portable `.openai-plugin/plugin.json` carries the OpenAI listing, `mcp.json` the hosted server, and `python3 scripts/validate_package.py --archive <zip>` builds the directory upload. The plugin shares one version with every other host (0.4.0 at the move).

**October 15 update (DITTO-855):** Peyton confirmed Omni Aura LLC, support@heyditto.ai, subscription management at https://app.heyditto.ai, and https://heyditto.ai/privacy. Launch intent is all legally and platform-permitted markets; the OpenAI draft now uses `countries: []` to remove publisher-added restrictions per the current field reference. This does not certify legal eligibility. The common skill now comes from private `ditto-assistant/ditto-skills`, with separate host adapters. Older pending values and versions below are historical; current manifests and the DITTO-855 Confluence submission-copy page supersede them. No store submission is authorized.

**MCP correction (DITTO-893):** Both packages now use https://api.heyditto.ai/mcp with host-managed sign-in. Claude 0.3.0 removes the prior CLI bootstrap, commands and lifecycle hooks. Native Claude shows the installed plugin with two skills and one connected Ditto MCP connector. Current OpenAI version is 0.1.4. Installation/discovery are verified; actual memory execution, music playback and store submissions remain separate.

October 12, 2026. Romanee Spencer, Chief of Staff and Operations at Omni Aura, coordinates business/listing metadata. Peyton remains technical/release owner; specific engineering owners must be confirmed.

Jira: https://omniaura-team.atlassian.net/browse/DITTO-764
OpenAI source: https://github.com/ditto-assistant/ditto-plugins (plugins/ditto/plugin.json)
Claude source: the same repository (formerly ditto-claude-plugins)
Archived prototype reference: https://github.com/ditto-assistant/chatgpt-store-app

The OpenAI repo is private preparation source, not a live directory listing. Claude's repo/package already exists. Keep current submission identities; a ZIP/local install is not live-host or publication proof.

## Shared publisher and business facts

| Field | Value or completion rule | Owner |
| --- | --- | --- |
| Publisher / company | Use Omni Aura as the requested publisher; verified portal identity and current legal entity still need confirmation. | Romanee + authorized developer |
| Product / category | Ditto; Productivity is the existing draft category. Confirm each portal's available categories. | Romanee |
| Contact | support@heyditto.ai is in the existing Claude manifest; confirm monitored submission/review contact. | Romanee |
| Website / docs / policies | Existing OpenAI draft uses heyditto.ai/, /contact, /privacy and /terms. Recheck public content and plugin-specific data coverage before submission. | Romanee + legal/product |
| Commerce | Start free, then optionally subscribe for more storage. Exact checkout/payment location and current pricing need confirmation. | Romanee + Peyton |
| Markets / translations | Reuse 'where Ditto is available'; reconcile the earlier 244-code draft with current backend restrictions and host-supported markets. Translations optional. | Romanee + engineering |
| License / source rights | Claude existing manifest declares MIT. Do not infer the OpenAI release license or rights to additional assets. | Maintainer |
| Data practices | Confirm actual personal-data use/storage, external destinations, retention/deletion and under-18 targeting. Do not invent policy answers. | Peyton + legal/product |

## OpenAI package and listing fields

| Field | Value or completion rule | Owner |
| --- | --- | --- |
| $schema, name, version, description | Portable root plugin.json; retain ditto / 0.1.0 draft identity. name <=64; summary <=4000; use explicit version. | Engineering + Romanee |
| author.name / email / url; homepage; repository; license; keywords | Publisher and project metadata. repository points to ditto-plugins. Optional fields remain absent if unconfirmed. | Romanee |
| interface.displayName | Ditto; <=30 characters. | Romanee |
| interface.shortDescription | Recall and save Ditto memories; 30 characters, <=30. | Romanee |
| interface.longDescription | <=4000; factual memory search/fetch, related subjects and user-requested summaries. Exclude untested native-chat sending, full-history or UI claims. | Romanee + engineering truth check |
| interface.developerName / category / capabilities | Requested Omni Aura; verified identity governs public name. Productivity draft. Capability labels <=20, each <=120; Codex compatibility requires the field. | Romanee + engineering |
| interface.websiteURL / supportURL / privacyPolicyURL / termsOfServiceURL | Four public HTTPS pages for MCP review; <=1024 each. homepage/author.url do not populate these. | Romanee |
| interface.defaultPrompt | Up to 3 unique starter prompts, <=128 characters each; reuse existing three memory prompts. | Romanee + skills |
| interface.logo / composerIcon | Contained existing Ditto icon paths; verify actual file size/dimensions, logo >=256 square and composer >=48 square for submission. | Romanee + design |
| interface.logoDark / composerIconDark / brandColor / brandColorDark / screenshots | Optional assets/colors/screenshots; do not block on unrequested dark variants. | Romanee + design |
| onboardingSkill | Optional packaged skill path. Reuse memory skill; add getting-started only if needed. | Skills + engineering |
| review.test_cases.positive / negative | Single server: 5 positive and 3 negative cases for initial MCP review. Existing draft cases are NOT RUN. | QA + Romanee |
| Case description / prompt / tools_triggered / expected_behavior | Every case has description and prompt; positives need expected tools/result. Optional file_attachment_urls / expected_output_url. Negative no-action expectations must be explicit. | QA |
| review.demo_recording_url | Actual accessible walkthrough link, currently missing. Script/screenshots alone do not fulfill recording evidence. | QA + Romanee |
| review.commerce / commerce_description | Keep commerce here, not publication. Existing true declaration and storage-subscription wording need checkout detail. | Romanee |
| publication.countries / release_notes / translations | Country allowlist and version notes; optional locale subtitle <=30 and description <=4000. Preserve omission vs empty-list semantics. | Romanee |
| mcp.json | Existing HTTPS Streamable HTTP endpoint api.heyditto.ai/mcp. Hosted OAuth; no literal credentials, Claude-only interpolation or public-upload hooks/app bindings. | Engineering |

## OpenAI portal-only setup and review

| Field | Value or completion rule | Owner |
| --- | --- | --- |
| Organization / project / verified developer | Authorized publishing account and intended business identity; confirm whether any prior draft/listing exists. | Peyton + Romanee |
| MCP server connection / OAuth / domain verification | Connect real submitted server, validate OAuth/scopes and domain challenge without overwriting unrelated challenges. | Engineering + authorized developer |
| Reviewer account / login URL / workspace / access instructions | Dedicated populated test account, stored in secure portal fields only. Current official guidance says it must work without MFA/email-code/magic-link/private-network dependence. | QA + authorized developer |
| Imported metadata / skills scans / tool findings | Check the saved version, deployment annotations and all scan results. ZIP validation does not prove live tools or UI. | Engineering + QA |
| Policy attestations / Submit for review / Publish | Authorized developer supplies truthful attestations. Draft upload, review approval and publication are separate; nothing submitted/published here. | Authorized developer |

## Claude plugin manifest and marketplace

| Field | Value or completion rule | Owner |
| --- | --- | --- |
| .claude-plugin/plugin.json: name | Existing ditto; directory identifier <=64 ASCII lowercase letters/digits/hyphens, no conflicting brand/name. | Maintainer |
| displayName / description / version / author | Current version 0.3.0, author Ditto (Omni Aura), description for hosted MCP memory and shared music curation. No automatic Code hook behavior. | Romanee + engineering |
| homepage / repository / license / keywords | Current site and Claude repo; existing MIT and keywords. Keep product website separate from directory docs URL. | Romanee |
| icon / documentationUrl / supportUrl / privacyPolicyUrl / termsOfServiceUrl | Directory values go in plugin.json, not marketplace entries. Current manifest lacks these five listing fields; prepare actual assets and public URLs. | Romanee + maintainer |
| README / install and privacy guidance | Directory description comes from plugin-folder README; ensure meaningful copy, setup, limits, support and current data practices. | Romanee + skills |
| Marketplace name / owner / plugins[].name / source / category | Preserve existing ditto-claude-plugins marketplace and ./plugins/ditto source path. | Maintainer |
| skills / commands / agents / hooks / mcpServers / lspServers / userConfig | The package has two shared skills and .mcp.json for the hosted Ditto HTTP MCP server. CLI bootstrap, commands, agent provisioning and hooks are removed. Validate actual host-managed OAuth and tool behavior. | Engineering + skills |

## Claude plugin submission form

| Field | Value or completion rule | Owner |
| --- | --- | --- |
| Repository / Plugin path / Branch or tag | Existing ditto-assistant/ditto-claude-plugins; plugins/ditto; confirm tracked release branch/tag. Connected submitter must be able to push; source must be public to go live. | Maintainer + authorized submitter |
| Listing details | Preview values from manifest and README; edit source and revalidate rather than typing unsupported extra manifest fields. | Romanee + maintainer |
| Data handling | Whether personal data is read/stored, sent beyond declared connectors, retention and under-18 intent. | Peyton + legal/product |
| Compliance contact / four acknowledgments | Confirm contact email; authorized developer reviews actual acknowledgments, not pre-checked by an agent. | Authorized submitter |
| Update delivery / auto-publish | Choose GitHub webhook vs scheduled checks and explicitly decide publication settings; webhook setup requires repo admin. | Maintainer + authorized submitter |

## Claude paired remote connector form

| Field | Value or completion rule | Owner |
| --- | --- | --- |
| Connection | Hosted server HTTPS URL; only choose multiple-URL/pattern modes if needed by actual deployment. | Engineering |
| Tools | Live synced tools/prompts/resources, titles and read/write annotations; not manually fabricated. | Engineering |
| Listing | Server name <=100, one-liner <=200, description <=2000; 1–5 categories; docs URL, privacy URL, support contact, icon and stable listing slug. | Romanee |
| Use cases / prerequisites / read-write behavior | Memory retrieval/inspection and user-authorized save; required account/plan and scopes. | Romanee + engineering |
| Company / website / primary review contact | Confirm business details and contact. | Romanee |
| Authentication | Actual supported OAuth client registration/metadata mode and token checks; no credentials in public docs. | Engineering |
| Data handling | First-party/authorized proxy status; health-data and sponsored-content questions need factual answers. | Peyton + legal/product |
| Test & launch / reviewer credentials / compliance | Populated reviewer account and secure instructions; actual each-tool tests; authorized developer handles seven acknowledgments. | QA + authorized submitter |
| MCP App carousel / allowed links | If UI is submitted: 3–5 PNG response-only screenshots, >=1000px wide, paired prompts separately; optional owned-origin/scheme allowlist for UI link opening. | Design + QA + engineering |

## Engineering delivery map

| Existing issue | Work | Concrete next step |
| --- | --- | --- |
| [DITTO-423](https://omniaura-team.atlassian.net/browse/DITTO-423) | Existing MCP Apps memory UI | Reuse backend memory dashboard source noted in DITTO-758; prove deployed host rendering and account/Space boundaries. |
| [DITTO-758](https://omniaura-team.atlassian.net/browse/DITTO-758) | Codex Home/global entrypoint | Keep listing URLs distinct from global entrypoints; verify Home launch, new-draft actions, version/capability support and fallback. |
| [DITTO-424](https://omniaura-team.atlassian.net/browse/DITTO-424) | OpenAI packaging/directory | Use new private ditto-openai-plugins release repo; preserve existing backend/OAuth and ditto-mcp bridge. |
| [DITTO-425](https://omniaura-team.atlassian.net/browse/DITTO-425) | Claude plugin + connector | Use the MCP-backed Claude 0.3.0 package; finish listing metadata and actual host tool tests. No CLI auto-installer remains. |
| [DITTO-426](https://omniaura-team.atlassian.net/browse/DITTO-426) | Security and cross-host QA | Evidence for authorization, revocation/isolation, UI resources/CSP, unsupported-host fallback and actual first-user flow. |
| [DITTO-427](https://omniaura-team.atlassian.net/browse/DITTO-427) | Setup docs/launch register | Record source version, host support, submission state, real listing URL, and reviewer/adoption evidence. |

## Listing draft and next decisions

OpenAI display name: Ditto. Subtitle: Recall and save Ditto memories.

Draft description: Bring your Ditto memory into ChatGPT and Codex. Search saved knowledge, inspect supporting memories and related subjects, and save a useful summary when you ask. Sign in to your Ditto account. Start free, with optional paid storage through Ditto. Native Ditto chat sending and automatic full-history access are not promised. Final UI/Home claims await actual host evidence.

Resolve: exact checkout/payment location; verified developer identity/current legal entity; approved policy coverage and retention; actual reviewer access/recording; engineering owners and release date. Confirm existing portal drafts before creating submissions. Optional translations/dark assets are not blockers.

Skills: reuse the existing OpenAI ditto-memory skill and Claude Code skill. The generic skill recalls relevant bodies, captures durable context when the user requests or authorizes ongoing private capture, updates matching records with provenance and verifies write receipts. It does not inherit personal policies, identities or memory indexes. Keep live schema discovery and scoped evidence; test actual host MCP authentication and tool execution before making capability claims. Business copy waits for engineering confirmation of supported capabilities.

## Evidence and sources

- OpenAI submission and field reference: https://developers.openai.com/plugins/deploy/submission
- OpenAI package structure: https://developers.openai.com/plugins/build/plugins
- OpenAI UI: https://developers.openai.com/plugins/build/chatgpt-ui
- Claude manifest: https://code.claude.com/docs/en/plugins-reference
- Claude plugin form: https://claude.com/docs/plugins/submit
- Claude pre-submission: https://claude.com/docs/plugins/pre-submission-checklist
- Claude remote connector form: https://claude.com/docs/connectors/submit
- Current repo README/manifests and existing DITTO-422–427/758, read October 12.

Current source state: OpenAI draft review cases NOT RUN; no walkthrough recorded, no reviewer account verified, no directory submission/publication claimed. GitHub issue tracking exists for both repos. This account can maintain the new OpenAI repo but has read-only source access to the existing Claude repo; maintainer must land Claude changes. Peyton's admin access to the new OpenAI repo was verified; collaborator access on the existing Claude repo was not inspectable by this account.

