---
name: diagnose-bug
description: Find the root cause of a bug or slowdown with a reproduce-and-test loop, using past incidents in Ditto.
---

# Diagnose a bug

Find the cause before changing anything. A fix without a cause is a guess, and a
guess that happens to make the symptom disappear is the most expensive kind.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.
If this host gives you a local shell and the code is in a repository you can
run, also read [coding-agent.md](references/coding-agent.md). In a chat app,
skip it: the user runs each step and shares the result with you.

## 1. Recall

Search Ditto for the error text, the component and earlier incidents with similar
symptoms. A previous root cause, a known flaky dependency or a recorded gotcha
can save hours. Treat a recalled cause as a hypothesis to test, not an answer.

## 2. Reproduce

Get a reliable reproduction before anything else: the smallest input, command or
sequence that shows the failure, with the exact environment (versions or
branch, data, settings). If the bug is intermittent, find out how often it
happens so a fix can later be told from luck. If it cannot be reproduced, say so and gather evidence
(logs, screenshots, the user's exact steps) instead of guessing. When the user is
the one running things, give one exact step at a time and ask for its output.

## 3. Hypothesize and test

List the candidate causes and, for each, the observation that would rule it in
or out. Test the cheapest discriminating one first. Change one thing at a time.
Prefer evidence that can fail: a log line that would show a different value, a
comparison between a known-good and known-bad version, a stripped-down case.
A check that could only ever pass proves nothing.

When a hypothesis survives, confirm it from both sides: the failure appears when
the cause is introduced, and disappears when it is removed.

## 4. Fix and guard

Fix the cause, not the symptom. Add a regression test that fails on the unfixed
version and passes on the fixed one, and see it run both ways (in a chat app,
ask the user to run it before and after the fix). Remove any temporary logging added
to test hypotheses. If the fix is a workaround, say so plainly.

## 5. Report and remember

Report the symptom, root cause, evidence, fix and remaining risk, keeping what
was observed separate from what you inferred. Offer to save the incident to
Ditto (symptom, cause, fix, how it was found) so the next occurrence starts from
it. Save only when the user agrees, and exclude secrets and customer data.
