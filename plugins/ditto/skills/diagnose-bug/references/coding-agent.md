# Diagnose a bug: coding-agent additions

Read this only when you have a local shell and can run the code. In a chat app,
skip it.

- Run the reproduction yourself and record the command, branch, commit, data
  and flags. For an intermittent failure, run it enough times to state a rate.
- Use `git bisect` (or a manual binary search over commits) between a
  known-good and known-bad version when the regression window is unclear.
- Add temporary logging or assertions to discriminate hypotheses, and remove
  them before you finish.
- Write the regression test in the project's existing test setup and run it
  both ways: red on the unfixed code, green on the fix.
- Reproduce a suspected regression on the base branch in a separate checkout
  before believing your own change caused it.
