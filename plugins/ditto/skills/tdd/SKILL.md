---
name: tdd
description: Build features and fix bugs test-first with red-green-refactor, proving every new test can fail.
---

# Test-driven development

Write the test that describes the behavior, watch it fail for the right reason,
make it pass with the simplest change, then clean up. Repeat in small steps.

Use the bundled `ditto-memory` skill for connection, recall and capture rules.
This skill describes work the host may perform in a user's repository. Running
tests requires a separately available, authorized host execution tool; the
Ditto plugin bundles no executable code or test runner, and its declared MCP
server is used only for memory. If the host lacks execution access, describe
the tests to run and leave their result unverified.

## Before starting

Search Ditto for the project's testing conventions: the test runner and command,
fixture and mocking habits, and known traps. Then confirm them against the
repository itself; the repository wins when they disagree. Find the existing
test closest to what you are about to write and follow its shape.

## The loop

1. **Red.** Write one test for one behavior, named for the behavior rather than
   the implementation. Run it and read the failure. It must fail because the
   behavior is missing, not because of a typo, an import error or a broken
   fixture.
2. **Green.** Make the smallest change that passes. Run the whole relevant suite,
   not only the new test.
3. **Refactor.** Remove duplication and improve names with the tests green.
   Run them again after each change.

Keep steps small enough that a failure points at the last change. Commit at
green when the user wants commits.

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
