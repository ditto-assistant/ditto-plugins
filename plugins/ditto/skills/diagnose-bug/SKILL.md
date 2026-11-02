---
name: diagnose-bug
description: Find the root cause of a bug or slowdown with a reproduce-and-test loop, using past incidents in Ditto.
---

# Diagnose a bug

Find the cause before changing code. A fix without a cause is a guess, and a
guess that happens to make the symptom disappear is the most expensive kind.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.

## 1. Recall

Search Ditto for the error text, the component and earlier incidents with similar
symptoms. A previous root cause, a known flaky dependency or a recorded gotcha
can save hours. Treat a recalled cause as a hypothesis to test, not an answer.

## 2. Reproduce

Get a reliable reproduction before anything else: the smallest input, command or
sequence that shows the failure. Record the exact environment (versions, branch,
data, flags). If the bug is intermittent, measure how often it happens so you can
later tell a fix from luck. If you cannot reproduce it, say so and gather
evidence (logs, traces, the user's exact steps) instead of guessing.

## 3. Hypothesize and test

List the candidate causes and, for each, the observation that would rule it in
or out. Test the cheapest discriminating one first. Change one thing at a time.
Prefer evidence that can fail: a log line that would show a different value, a
bisect between a known-good and known-bad version, a stripped-down test case.
A check that could only ever pass proves nothing.

When a hypothesis survives, confirm it from both sides: the failure appears when
you introduce the cause, and disappears when you remove it.

## 4. Fix and guard

Fix the cause, not the symptom. Add a regression test that fails on the unfixed
code and passes on the fixed code; run it both ways. Remove temporary
instrumentation. If the fix is a workaround, say so plainly.

## 5. Report and remember

Report the symptom, root cause, evidence, fix and remaining risk, keeping what you
observed separate from what you inferred. Offer to save the incident to Ditto
(symptom, cause, fix, how it was found) so the next occurrence starts from it.
Save only when the user agrees, and exclude secrets and customer data.
