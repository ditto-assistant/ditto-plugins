# Owned workspace and build cleanup

Use this only with actual local inspection capabilities. A browser file upload
or cloud sandbox does not grant access to the user's Mac. Never substitute host
transcript databases, plugin caches or arbitrary directories for an owned task
workspace. Do not run a global cleanup sweep as a side effect of handoff.

## Inventory and recovery gates

Record a timestamp, filesystem free space (`df -h /System/Volumes/Data` on macOS,
or the actual workspace filesystem elsewhere), canonical candidate paths and
`du` sizes. Avoid double-counting nested checkouts. Establish ownership from the
current task, managed-worktree attachments and repository metadata, not names
or age. Exclude other sessions, primary/shared/pinned/active checkouts and source
data. Resolve symlinks; do not cross into another checkout.

Inspect tracked, staged, untracked AND ignored files, local branches, stashes and
worktrees. A clean `git status` omits ignored files. Separate reproducible builds
from unique fixtures, databases, uploads, screenshots, configuration and recovery
material. Do not expose secrets. Never assume an ignored file is disposable.

Before removing a checkout, make valuable code durable through its delivery
rules. Pushing code, creating a remote or opening/updating a PR requires existing
user/repository authority for that action and destination; handoff or disk cleanup
alone grants none. If authority or destination is missing, retain the checkout
and ask for the exact preservation plan. Do not upload private work just to make
cleanup possible. This deferral need not block a verified memory save or chat
archive. When push/PR delivery is authorized, commit and push, open/update the PR
and verify remote head against local commit. Read the
PR's actual base, state, validated head and merge receipt. A merged PR does not
prove later local changes landed; squash merges also mean branch-tip ancestry
alone is insufficient. Open PRs stay by default. Closed/merged state is not
deletion permission. Preserve unique branches, stashes, untracked files and needed
ignored files durably, unless the user explicitly chooses to discard the identified
material with its loss understood. For preserved material, verify recovery and
record restore instructions. A backup is not mandatory for an authorized discard.
Do not push secrets just to obtain a clean checkout. A summary is not a backup.

## Scope and mechanism

If the user's cleanup instruction does not cover the exact owned candidates,
present paths, sizes, preservation/recovery plan and proposed operations for
approval. Do not re-ask for exact operations already authorized. No deletion
follows merely because a handoff exists. Do not discard unique unpushed/uncommitted
work or source data without explicit authority for those identified files.

Choose the mechanism within the user's scope:

* **Direct deletion, no archive:** valid when the user wants the files gone.
  For clean, durably pushed code and reproducible temporary/build artifacts,
  verify the evidence and remove the exact owned paths. Do not create a recovery
  archive or require backup approval anyway. If unique local material is present,
  identify what would be lost and either preserve it or obtain explicit discard
  authority; do not silently destroy it or silently create an unwanted backup.
* **Recoverable worktree archival:** use the host's managed archive-worktree
  mechanism when recovery is wanted or required by that host. Inspect its live
  contract and attachment identity, preserve needed ignored files separately,
  and verify the snapshot/restore receipt. It does not establish backup of ignored
  files. Do not bypass a host refusal or primary/pinned/shared protection with raw
  recursive deletion. If the host only supports archival but the user requires
  deletion without a snapshot, disclose that limitation instead of making one.

For ordinary Git worktrees use supported removal only after all gates pass.
For task clones and temporary builds, remove only exact approved, inventoried
owned paths using a suitable filesystem tool. Never run arbitrary recursive `rm`,
broad `find ... -exec rm`, wildcard worktree purges or deletion by age/name.
Never remove app data, source databases, Docker volumes, global caches, primary
checkouts or another session's artifacts under this skill. Follow a separately
authorized exact cleanup plan for those.

Before stopping a process, establish PID, command, working directory and relation
to this task. Stop only owned build/preview processes; never kill by executable
name. Preserve resumption evidence first. Retain artifacts with active writers
or consumers and record the reason.

## Verify results

Inspect each archive/removal receipt and actual path state. Measure free space
again; report before/after timestamps and actual reclaimed space or uncertainty
(snapshots/open files can delay visible free space). Do not claim a `du` estimate
as actual free space gained. Verify preserved files/snapshot references and a
practical restoration path for material intended to survive, including remote
repository, branch/commit, PR and private backup location as applicable. For direct
deletion, record that no archive was made and which local artifacts were discarded;
do not invent a restore path or describe deleted-only data as recoverable.

Update the Ditto handoff with results and verify the update. Keep filesystem
cleanup and chat archival receipts separate. If removal or recovery verification
fails, retain remaining material, identify the failure and do not broaden deletion.
