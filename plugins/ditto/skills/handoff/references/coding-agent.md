# Handoff: coding-agent additions

Read this only when the host gives you a local shell or filesystem and the chat
worked in a repository, task workspace or local files. In a chat app, skip it.
Everything here adds to the main skill; it does not replace its save, readback
and archive gates.

## Add the workspace to the note

Include what a later session needs to resume or recover the code:

- repository, branch, workspace or worktree path, and exact commit SHAs;
- pull requests and CI runs with their state at the head you checked;
- validation evidence, keeping source, merge, deployment and live behaviour as
  separate facts;
- owned processes still running (dev servers, builds), and why;
- the disk and cleanup disposition below, including anything deferred and why.

Make code recoverable before you call it handed off. A memory note is not a
backup: code that exists only in an uncommitted or unpushed local checkout is
still at risk. Push or open a pull request only where the user or repository
rules already authorize it; a handoff alone grants neither. If that authority
or destination is missing, keep the checkout and say so in the note.

## Disk

Disk is a closeout concern when the machine is short of space or the task made
large builds. Only then, measure free space and the size of this task's own
workspace and temporary builds before deciding anything. If you cannot inspect
the filesystem, record that rather than inventing a number. Archiving a chat
does not reclaim disk and does not authorize deleting its workspace.

Read [workspace-cleanup.md](workspace-cleanup.md) before deleting or archiving
any local files.

## Reclaim only authorized material

After the Ditto readback passes, perform only cleanup the user already
authorized for exact owned paths that pass the cleanup reference's gates.
Otherwise present the measured candidates, sizes and plan, and keep the files.
Direct deletion without a backup is a valid user choice; do not force an
archive on a user who asked to just delete. Identify any unique local material
before it is discarded.

A cleanup failure does not invalidate a verified memory: report it separately
and keep a usable recovery path. Save the cleanup outcome and recovery locations
into the handoff and verify that update before archiving the chat.

## Receipts

Add the cleanup result (bytes reclaimed, or the deferral reason) to each chat's
receipt. Do not install shell memory helpers, new hooks or transcript capture
as part of a handoff.
