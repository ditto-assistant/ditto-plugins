# Code review: coding-agent additions

Read this only when you have a local shell and the change is in a repository you
can open. In a chat app, skip it.

- Build the diff yourself against the merge base of the branch the change will
  merge into, not an older branch, or you will review someone else's work.
- Read whole files around each hunk, plus callers and tests of what changed.
- Check whether each issue is new in this change or already on the base branch,
  and say which.
- Run the project's own tests, type checker or linter when that is cheap and
  confirms or refutes a finding. Use the commands the repository documents.
- Do not edit, commit or push while reviewing unless the user asks for fixes.
