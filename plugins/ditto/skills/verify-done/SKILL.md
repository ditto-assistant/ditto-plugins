---
name: verify-done
description: Check each claim before reporting work done: built, merged, deployed and working are separate facts.
---

# Verify before saying done

"Done" is a claim, and each part of it needs its own evidence. Most confident
wrong answers come from letting one piece of evidence stand in for another.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.

## Separate the claims

Split the report into the claims it actually makes, and check each one:

- **Written:** the change exists in the files or document, in the right place.
- **Builds and tests pass:** at the exact version you are describing, from the
  runner's own summary, not its exit code alone.
- **Reviewed and merged:** on the target branch, not only approved.
- **Deployed:** the running system serves this version. Read the version it
  reports instead of assuming a pipeline succeeded.
- **Works:** someone exercised the behavior the user cares about, in the place
  they will use it.

Report each separately. Saying "merged" when you mean "works" is the failure
this skill exists to prevent.

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
