# Verify done: coding-agent additions

Read this only when you have a local shell and the work is in a repository. In a
chat app, skip it.

- **Written:** `git status` and the full `git diff HEAD` (staged and unstaged)
  show the change, and only the change, in the intended clone and branch.
  Before claiming it is pushed, compare `git rev-parse HEAD` with
  `git ls-remote origin <branch>`; a local tracking ref can be stale.
- **Checked:** read CI results attached to the current pull request head
  commit, not an older run. A cancelled run can render as a failure, and a
  required check that never started is not green.
- **Approved and landed:** the pull request state is merged and the merge
  commit is on the target branch. With squash merges, branch ancestry alone
  does not prove it.
- **Live:** read the version or build endpoint the running service exposes,
  and compare it with the merge commit.
- Scripts that verify then commit need to stop on the first failure (for
  example `set -e` in shell); otherwise a failed build can still be pushed.
