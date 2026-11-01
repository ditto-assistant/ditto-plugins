---
name: handoff
description: Save verified continuation context to Ditto before closing one or more authorized chats, and assess safe cleanup of the agent's own workspace and build artifacts when disk space matters.
---

# Handoff

Preserve useful context, make code and files recoverable, and close out only the
authorized chats. Use `/handoff` where supported, or invoke this skill by name.
A draft or summary request alone does not authorize saving or archival. A full
handoff request authorizes private save and archival of the invoking chat; an
explicit bulk request covers only the selected set. It does not itself authorize
file deletion, messages to other chats, merging, deployment or ongoing capture.

## Establish scope and capabilities

Finish already-authorized work or record its blocker. Identify the invoking chat
from trusted host context, never recency or a similar title. For bulk requests,
inventory the selected set with stable host IDs, status and exclusion reasons.
Keep active, shared, pinned and unresolved recovery work unless explicitly
selected by the user and its remaining work can be preserved. Start with one
chat at a time; use concurrency only for an explicitly requested bounded batch.
Do not dispatch messages to every chat merely to gather handoffs.

Inspect available tools and fresh UI state. Ditto MCP stores the note; host tools
or UI manage host chats and local workspaces. Do not invent archive APIs, edit
host databases or count exiting a CLI as archival. Browser-only ChatGPT cannot
inspect or delete local files without a suitable authorized local filesystem or
computer tool. Disclose missing capabilities and continue independent steps.
Missing local inspection does not block an otherwise verified save and archive.
Preserve MCP and host-managed sign-in; do not install shell memory helpers,
new hooks or transcript capture.

## Preserve the continuation and assess disk

Write a concise note containing:

* Objective, durable decisions, constraints and scope of authorization.
* Completed work with exact issue, PR, source, artifact and commit references;
  repository, branch and workspace paths needed to resume or recover.
* Validation evidence, separating source, merge, distribution, installation,
  deployment and actual functional behavior. Preserve limitations and failures.
* Open work, owners, blockers, approvals and concrete recovery/next steps.
* Disk inventory and cleanup disposition: measured candidates, preserved files,
  recovery locations, owned processes, approved actions and deferrals with reasons.

Disk pressure is a core closeout concern, especially on machines with recurring
low space. With authorized local inspection, measure free space and the agent's
own task/worktree and temporary builds before deciding what to reclaim. Read
[workspace-cleanup.md](references/workspace-cleanup.md) before filesystem cleanup.
If inspection is unavailable, record that rather than inventing a measurement.
Archiving a chat does not establish that disk space was reclaimed.

Use current evidence; exclude transcripts, credentials and unnecessary sensitive
details. Mark outstanding archival/cleanup as pending. A memory summary is not
a backup of code or files.

## Save and verify through Ditto

Use bundled `ditto-memory` guidance and live MCP schemas. Verify the intended
account/private destination before writing. Use a known memory ID or search for
an existing handoff for this host/chat. Where supported, use a stable identity
derived from the host and actual chat ID, such as `handoff:<host>:<chat-id>`.
Never fabricate an ID or URL. Update an owned matching record rather than
duplicating it; do not rewrite another author's record.

Save the note, inspect the receipt, then fetch its full content by returned ID.
Compare all intended content and critical references with the draft; a receipt,
title, search snippet or successful fetch alone is insufficient. Verify every
part if size limits require splitting. Search indexing may lag. If a write times
out, reconcile by returned ID or supported stable identity before retrying;
do not blindly repeat it. If ambiguity remains, stop that item's closeout.

If save or exact readback fails, leave that chat open and preserve code/files.
Return the draft and the specific failure. Never put private handoffs in the
skill repository or plugin package. A local note is not the Ditto save gate.

## Reclaim only authorized material

After successful readback, perform only cleanup already authorized for exact
owned candidates and passing the cleanup reference's preservation or discard gates. Otherwise
present the measured scope for approval and retain the files. Archiving chats
does not authorize deleting their workspaces. Cleanup failure does not invalidate
a verified memory: report it separately and preserve a usable recovery path.
Direct deletion without a recovery archive is a valid user choice. When the user
asks to just delete, do not make an archive or backup a prerequisite. Verify
remote durability for code being retained and identify any unique local material
being discarded; do not infer permission to discard it from a memory summary.
Save material cleanup outcomes/recovery locations into the handoff and verify
that update before archiving.

## Archive and record receipts

Prefer a documented implicit-current-chat archive operation. Other targets need
a trusted stable ID and explicit selection. If tools are absent, use supported
UI only when fresh state identifies the exact chat and archive action. If neither
is available, retain the saved handoff, report `archive unsupported`, and give
the manual host closeout step. Never claim archival from memory save.

For each selected chat keep a receipt with host/chat identity, memory IDs,
readback result, archive result and cleanup result/bytes or deferral reason.
Distinguish `saved and verified`, `already archived`, `archive failed`,
`unsupported`, `save uncertain` and `readback failed`. On retries, reconcile both
the memory and current archive state; do not duplicate or toggle blindly.
An already archived chat without a verified handoff remains a gap, not a success.
Leave failed items open when possible and continue independent selected items;
stop the batch for account mismatch, scope uncertainty or a user stop request.

Before each archive, persist the known receipt state in that chat's verified
private handoff or an authorized private batch ledger, including the memory ID
and stable chat ID for restart. Keep post-archive receipts in the host or batch
ledger; never claim that the final self-archive result was saved beforehand.

Complete tracker updates and expose recoverable receipts before archiving the
invoking chat, since that may end interaction. In bulk runs, process it last.
Archive each item only after its own save/readback gate. Inspect the archive
receipt or refreshed host state before reporting success; reconcile ambiguous
results before retrying. The invoking chat's archive is the final mutation.
