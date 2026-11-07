---
name: tdd
description: Build features and fix bugs test-first with red-green-refactor, proving every new test can fail.
---

# Test-driven development

Write the test that describes the behavior, watch it fail for the right reason,
make it pass with the simplest change, then clean up. Repeat in small steps.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.
If this host gives you a local shell and a repository you can run, also read
[coding-agent.md](references/coding-agent.md). In a chat app, skip it: give the
user the test first and ask for the runner's red output, then the code and its
green output.

## Before starting

Search Ditto for the project's testing conventions: the test runner and command,
fixture and mocking habits, and known traps. When the user shares an existing
test close to what you are about to write, follow its shape. Ask for one if the
project's conventions are unknown.

## The loop

1. **Red.** Write one test for one behavior, named for the behavior rather than
   the implementation. It must fail because the behavior is missing, not because
   of a typo, an import error or a broken fixture; read the failure to check.
2. **Green.** Make the smallest change that passes, then run the whole relevant
   suite, not only the new test.
3. **Refactor.** Remove duplication and improve names with the tests green, and
   run them again after each change.

Keep steps small enough that a failure points at the last change. Never claim a
test went red or green unless you or the user actually saw that result.

## Tests that can fail

A test is only evidence if it could have failed. Check each new test against the
unfixed code, or break the implementation on purpose and watch it go red. Pin
inputs, not computed values: a test that mocks the very value it asserts cannot
fail. Assert on observable behavior, not on private calls. A suite that reports
zero tests run, or exits zero while printing failures, is not a pass; read the
runner's summary line.

## Finish

Report which behaviors are covered, the command that runs them and the result.
When the work turns up a durable convention or trap (a flaky fixture, a slow
suite, a required flag), offer to save it to Ditto for next time.
