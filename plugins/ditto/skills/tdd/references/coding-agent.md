# TDD: coding-agent additions

Read this only when you have a local shell and can run the project's tests. In a
chat app, skip it.

- Confirm the remembered conventions against the repository: its documented
  test command, runner configuration and the existing test closest to yours.
  The repository wins when they disagree.
- Run each red and green step yourself and read the runner's summary line, not
  only its exit code.
- A new test that went red against the missing behavior has already shown it
  can fail. For a test that passed from the start, break the implementation
  with a small temporary edit, watch the test go red, undo that edit and
  confirm the diff is what you intended. Never use `git restore`,
  `git checkout` or a stash over uncommitted work to do it.
- Commit at green only when the user wants commits.
