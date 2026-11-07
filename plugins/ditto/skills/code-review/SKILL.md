---
name: code-review
description: Review a diff for correctness bugs first, applying the team's conventions remembered in Ditto.
---

# Code review

Find the problems that would hurt users or maintainers, and say each one so the
author can act on it. Correctness first, clarity second, style last.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.
If this host gives you a local shell and the change is in a repository you can
open, also read [coding-agent.md](references/coding-agent.md). In a chat app,
skip it and review what the user shares.

## Gather context

Review the diff the user pasted, uploaded or linked through a connected tool,
with as much surrounding code as you can see. Read the description or linked
issue to learn the intent. Search Ditto for the team's review conventions, past
review decisions about this area and known pitfalls; a convention the team
agreed on outranks your personal preference. If a finding depends on code you
cannot see, ask for that file or mark the finding as a question rather than
guessing. Say whether each issue is new in this change or already in the code it
modifies; when the shared context cannot tell, say so.

## Review in passes

1. **Correctness.** Wrong logic, missing cases, off-by-one, nil or empty inputs,
   error paths, concurrency, resource leaks, unsafe input handling, permission
   checks, data migrations and backwards compatibility.
2. **Tests.** Do the tests cover the new behavior, and could they fail if the
   code were wrong?
3. **Design.** Unneeded complexity, duplication of an existing helper, names that
   mislead, and changes in the wrong layer.
4. **Style.** Only what the project's formatter and linter do not already catch.

## Verify before reporting

For each candidate finding, trace the actual code path and try to construct the
failing input. Drop findings you cannot support. Mark a finding as a question
when you are unsure.

## Report

List findings most severe first. Each one names the file and line, the problem,
a concrete failure scenario and a suggested fix. Then give a short verdict. Do
not post comments, approve or request changes on a hosted review unless the
user asks you to. When the review settles a convention ("we always validate at
the handler"), offer to save it to Ditto, in the team's space if the user has
one.
