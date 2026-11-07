---
name: verify-done
description: Check each claim before reporting work done: built, merged, deployed and working are separate facts.
---

# Verify before saying done

"Done" is a claim, and each part of it needs its own evidence. Most confident
wrong answers come from letting one piece of evidence stand in for another.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.
If this host gives you a local shell and the work is in a repository, also read
[coding-agent.md](references/coding-agent.md) for the concrete checks. In a chat
app, skip it and check what the connected tools and the user can show you.

## Separate the claims

Split the report into the claims it actually makes, and check each one:

- **Written:** the change exists in the file, document or draft, in the right
  place.
- **Checked:** tests, builds or reviews passed for this exact version, read
  from their own summary rather than a green badge.
- **Approved and landed:** on the target branch, published or sent, not only
  approved or scheduled.
- **Live:** the running system or the published page serves this version. Read
  what it reports instead of assuming a pipeline succeeded.
- **Works:** someone exercised the behavior the user cares about, in the place
  they will use it.

Report each separately. Saying "merged" when you mean "works", or "scheduled"
when you mean "sent", is the failure this skill exists to prevent.

## Evidence that could have failed

A check proves something only if it could have come out the other way.

- A search that found nothing is evidence of absence only if the same search
  finds a known positive.
- A test is evidence only if it fails without the change.
- A status page or green badge may be cached, cancelled or for a different
  version. Check what it is attached to.
- A count next to "all clear" shows how much was actually inspected. Zero
  inspected is not a pass.

## Report honestly

State what you observed and what you inferred, in separate sentences. Name what
you could not check and why. If a later fact contradicts an earlier report, say
which claim it replaces. Search Ditto for this project's known false-green traps
before checking, and offer to save any new one you find.
