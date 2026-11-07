---
name: handoff
description: Save a verified continuation note to Ditto so the next conversation can pick up the work, then close the chat where the host supports it.
---

# Handoff

Write down what the next conversation needs, save it to Ditto, check that it
saved, then close the chat. Use `/handoff` where supported, or invoke this skill
by name. Keep it quick: a handoff is a short note, not an audit.

A draft or summary request alone does not authorize saving or closing anything.
A full handoff request authorizes a private save and archival of the invoking
chat. It does not authorize deleting files, messaging other chats, merging,
deploying or ongoing capture.

## Which path

- **Chat app** (Claude chat, ChatGPT, Cowork or any host without a local shell
  or repository): follow this file only. Work from the conversation itself. Do
  not inventory tools, inspect files, measure disk, check git or look for
  processes, and do not mention them in the note.
- **Coding agent** (Claude Code, Codex CLI, Cursor or any host with a local
  shell): follow this file. When the chat touched a repository or local files,
  also read [coding-agent.md](references/coding-agent.md) for workspace recovery
  and cleanup; otherwise treat it like a chat app.

## Write the note

Keep it concise and current:

- Objective, durable decisions, constraints and what was authorized.
- What was done, with the exact links and references from the conversation:
  documents, issues, tickets, messages, files shared.
- Evidence that it worked, kept separate from what was only planned, drafted or
  assumed. Keep limitations and failures.
- Open work, owners, blockers, pending approvals and the concrete next step.

Exclude transcripts, credentials and unnecessary sensitive details. A memory
note is not a backup of files or code.

## Save and verify through Ditto

Use the bundled `ditto-memory` guidance and the live MCP tool schemas. Check
that the connected account is the intended one. Search once for an existing
handoff for this chat; where the host exposes a real chat ID, use a stable
identity such as `handoff:<host>:<chat-id>`. Never invent an ID or URL. Update
your own matching record instead of duplicating it; never rewrite another
author's record.

Save the note, then fetch it by the returned ID and check its content and key
references against the draft. If size limits split the note, fetch and check
every part. A receipt, title or search snippet alone is not verification;
search indexing may lag. If a save times out, reconcile by the
returned ID or stable identity before retrying rather than saving twice.

If the save or readback fails, leave the chat open, give the user the draft and
the specific failure. A local file is not a substitute for the Ditto save, and
a private handoff never goes into a skill repository or plugin package.

## Close the chat

Close only after the readback passes. Use a documented archive operation for
the current chat when the host provides one. Otherwise use the host's own UI
only when you can see the exact chat and its archive action. If neither exists,
which is normal in chat apps, report the saved memory ID and tell the user to
archive the chat from the host's chat menu. Never claim the chat was archived
because the memory saved. Report `archived` only after the archive receipt or
refreshed host state shows it; reconcile an ambiguous result before retrying.

Give the user the receipt before archiving, since archiving may end the
conversation: memory ID, readback result and the archive step about to run (or
`unsupported`, `already archived`, `readback failed` or `save uncertain` when
none will). If the conversation continues after the attempt, report `archived`
or `archive failed`; in a batch, record it in the batch ledger. Do not archive
an already archived chat again.
Archiving the invoking chat is the last action.

## Several chats

Close out more than one chat only when the user names the set. Identify each by
a stable host ID, never by recency or a similar title, and keep active, shared,
pinned or unfinished chats unless the user selects them. Do one chat at a time:
its own note, save, readback and archive, with a receipt per chat. Leave a chat
that fails open and continue with the other selected chats. Before each
archive, save that chat's memory ID and stable chat ID in its verified handoff
or an authorized private batch ledger, so an interrupted run can resume without
duplicating saves or toggling archives. Do not send messages to every chat just
to gather handoffs. An already archived chat with no
verified handoff is a gap, not a success. Stop the batch on an account mismatch,
scope doubt or the user's request, and process the invoking chat last.
