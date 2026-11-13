# Lifecycle hooks

Ditto works best when an agent pulls memory before it starts and pushes the
outcome when it finishes. Skills can do both, but only when the agent remembers to
use them. Hooks are the host's own lifecycle events, so they can remind the agent at
those moments. This page records which hooks the plugin ships, why it ships those
and no others, and what each host actually supports (DITTO-2706).

## What ships

The plugin ships hooks for **Claude Code** only. They are wired through
`.claude-plugin/plugin.json` (`"hooks": "./hooks/claude-hooks.json"`), and every
handler runs `sh hooks/ditto-hook.sh <step>` with a 5-second timeout.

| Claude Code event | Step | What it does |
| --- | --- | --- |
| `PostToolUse`, matched only to Ditto's memory tools (`mcp__*ditto*__search_memories`, `fetch_memories`, `save_memory`, `update_memory`, `aggregate_memories`) | `connected` | Records, as an empty `connected` file in the plugin's data directory, that a Ditto memory tool has succeeded. It prints nothing. The host starts it only for those tools, never on other tool calls. |
| `SessionStart` (`startup`, `resume`, `clear`) | `session-start` | Adds about 100 words of context: search Ditto through the `ditto-memory` skill before work that depends on the user's history, treat memories as evidence rather than instructions, and save durable outcomes at the end if the user has authorized capture. |
| `PreCompact` | `pre-compact` | Its output becomes instructions for the compaction summary: keep Ditto memory IDs, and keep outcomes not yet saved to Ditto marked "not yet saved to Ditto". |
| `SessionStart` (`compact`) | `compact` | After compaction: reuse the memory IDs in the summary, and save the outcomes marked as unsaved if capture is authorized. |
| `Stop` | `stop` | Once per attended session and at most once a day, after real work, it asks the agent to save one concise note through `ditto-memory` if the user authorized capture. Otherwise the agent offers to save, in one sentence. |

**Silent until Ditto works here.** Until the `connected` file exists, every step
prints nothing. A user who installed the plugin but never connected the Ditto
server gets no added context and no Stop check. The first successful Ditto memory
tool call, whether from a skill, a user request or the agent's own choice, turns
the reminders on for that installation. An MCP error result does not count. Every
later Ditto call refreshes the file, and after 30 days without one it is removed,
so a user who disconnects or de-authorizes Ditto stops getting reminders.

The `stop` step stays silent unless all of these are true:

- the session is attended: someone is there to answer. Claude Code sets
  `CLAUDE_CODE_SESSION_ATTENDED=1` in an interactive terminal and `0` in
  `claude -p` and Agent SDK runs; older versions without that variable fall back
  to `CLAUDE_CODE_ENTRYPOINT=sdk-*` meaning unattended. Set `DITTO_HOOKS_STOP=1` to
  run the check in headless automations too.
- the host is not already continuing because of a stop hook (`stop_hook_active`)
- it has not already asked in this session, or in any session in the last 24
  hours. This cap means a user who declines is not offered capture in every
  session, and the text tells the agent not to re-offer once the user has said no.
- the local transcript shows a file edit (`Edit`, `Write`, `MultiEdit`,
  `NotebookEdit`) or at least ten tool calls
- the transcript shows no Ditto `save_memory` or `update_memory` call

Only the main session transcript is read. Edits made inside subagents land in
their own sidechain transcripts, so a session that delegates its file writes
counts only its `Task` calls toward the ten-call threshold.

When it does ask, it returns `hookSpecificOutput.additionalContext`. The host then
runs one extra short turn, and Claude Code shows it as a normal stop-hook step.
(`decision: "block"` would do the same, but the terminal labels its reason
"Stop hook error".) A marker file under the plugin's data directory
(`${CLAUDE_PLUGIN_DATA}`) keeps that to once per session. Markers older than 30
days are removed the next time the step writes one.

**Transcript format.** The check greps the local JSON Lines transcript instead of
parsing it. It counts a tool call when either `"type":"tool_use","id":"…","name":"X"`
or `"name":"X","input":` appears; tool *definitions* (`"name":"X","description"`)
never match. `tests/fixtures/claude-code-2.1.308-write.jsonl` is a real Claude
Code 2.1.308 line with its identifying values replaced, and a test keeps the check
firing on it and on reordered keys. If a Claude Code release changes that shape,
the check goes quiet (it fails open), so refresh the fixture from a current
transcript when updating the hooks.

### Safety properties

- **No network, no credentials.** The script prints fixed text. Its only other
  inputs are the hook's stdin and, for `stop`, a grep of the local transcript. It
  never calls Ditto: memory reads and writes go through the agent's own Ditto MCP
  connection and the host's usual tool permissions and OAuth, so they follow the
  same approval rules as any other tool call.
- **Fail-open.** Every path exits 0: the body runs in a subshell and the script
  ends with `exit 0`, so not even a shell error can return Claude Code's blocking
  exit code 2. (A test caught exactly that: under dash, a failed redirect on the
  `:` builtin exits the shell with 2.) Bad input, a missing transcript, a read-only
  data directory or an unknown step all produce no output, and the host carries
  on as if the hook had not run. Each handler has a 5-second timeout. In practice they
  finish in about 20–40 ms.
- **No logs.** The script writes nothing except empty marker files.
- **Opt-out.** `DITTO_HOOKS=0` turns every hook off. `DITTO_HOOKS_STOP=0` turns off
  only the end-of-task check, and `DITTO_HOOKS_STOP=1` turns it on in unattended
  sessions. `off`, `false` and `no` work as well as `0`; `on`, `true` and `yes` as
  well as `1`. In
  Claude Code, set the variable in the `env` block of `~/.claude/settings.json`, or
  disable the plugin with `/plugin`.
- **Pinned.** `scripts/validate_package.py` rejects any hook file whose SHA-256 is not
  pinned in `scripts/hook-allowlist.json`. It also rejects:
  - `hooks/hooks.json` at the default path
  - a hook declared in any manifest other than Claude's
  - any event, matcher or handler type outside this set
  - a timeout above 10 seconds
  - a command that does anything except run the bundled script
  - an executable bit on any plugin file
  - a hook file that names a network tool or a script interpreter

  CI runs this check on every PR. The ChatGPT upload carries no hooks.

### Not shipped, and why

| Candidate | Reason |
| --- | --- |
| `UserPromptSubmit` recall | Recall on every prompt is a network round trip and adds context to every turn. That is what 0.2.x did, and #5 removed it. The SessionStart reminder plus the skill gets the agent to search when the task needs it. |
| `PreToolUse`, or `PostToolUse` on every tool | Runs on every tool call. There is nothing for Ditto to do there that justifies the latency. The shipped `PostToolUse` entry is matched to Ditto's memory tools only, and the validator rejects any other matcher. |
| `SessionEnd` | It cannot reach the model, so it could only save memory by calling Ditto itself. That needs credentials in a script, which this plugin does not hold. Claude Code also limits it to 1.5 s. |
| `SubagentStop` | Saving is the parent agent's job. A check in every subagent would multiply the extra turns. |
| `mcp_tool` handlers | They would call Ditto with no query to search for at session start (Claude Code skips `mcp_tool` on SessionStart at launch anyway). At Stop, a bare save would be a transcript dump, which the memory skill forbids. |
| Automatic saving without asking | The `ditto-memory` skill saves only with the user's authorization ("ask before enabling ongoing capture"). Changing that is a product decision for the skill source, not for a hook. |

## Host support

Researched from each host's current documentation and the locally installed CLIs
on 2026-11-10. "Auto-loads `hooks/hooks.json`" means the host picks that file up from
the plugin folder without any manifest field. That is why this plugin never ships one.

| Host | Hook events relevant here | Auto-loads `hooks/hooks.json` | Status |
| --- | --- | --- | --- |
| Claude Code | SessionStart (with `compact`), PreCompact (output feeds the summary), Stop (`additionalContext` or block, `stop_hook_active`), PostToolUse with a tool-name matcher | Yes | **Shipped** |
| Codex | SessionStart (with `compact`), Stop (block). PreCompact output is ignored. | Yes, unless `.codex-plugin` sets `hooks` | Not yet. Hooks need per-user trust review, and a plugin ZIP with hooks cannot go to the OpenAI directory. A Codex-specific file, kept out of the ChatGPT upload, is a candidate follow-up. |
| Cursor | `sessionStart` (`additional_context`, fire-and-forget), `stop` (`followup_message`), `preCompact` (observe only) | Yes, unless `.cursor-plugin` sets `hooks` | Not yet. Different schema and transcript format. Candidate follow-up. |
| GitHub Copilot CLI / VS Code | `sessionStart` (top-level `additionalContext` only), `agentStop` (block), `preCompact` (notification only) | Yes (`hooks.json` or `hooks/hooks.json`) | Not shipped |
| Grok Build | SessionStart cannot add model context; Stop (block) | Yes | Not shipped: only the Stop check would carry over |
| Antigravity | SessionStart (`injectSteps`), Stop; no PreCompact | No (reads `<plugin>/hooks.json`) | Not shipped |
| Kimi Code | SessionStart is observe-only; Stop (block); UserPromptSubmit | Not documented | Not shipped |
| ChatGPT (web, desktop) | None for plugins: the Agent Plugins 1.0 format defines only skills and MCP servers | n/a | Skills only |

On every host without shipped hooks, the bundled skills (`ditto-memory`, `handoff`)
remain the way to pull and push memory. The validator keeps each of those hosts
from picking up the Claude file by accident: no file sits at a default path, and
only the Claude manifest may name a hook file. Cursor, Codex, Copilot and Grok
each read their own manifest first.

Sources: [Claude Code hooks](https://code.claude.com/docs/en/hooks),
[Claude Code plugins](https://code.claude.com/docs/en/plugins-reference),
[Cursor hooks](https://cursor.com/docs/agent/hooks),
[Codex hooks](https://developers.openai.com/codex/hooks),
[OpenAI plugins](https://developers.openai.com/plugins/build/plugins),
[Copilot hooks](https://docs.github.com/en/copilot/reference/hooks-reference),
[VS Code hooks](https://code.visualstudio.com/docs/copilot/customization/hooks),
[Antigravity hooks](https://antigravity.google/docs/hooks/),
[Kimi Code hooks](https://moonshotai.github.io/kimi-code/en/customization/hooks.html),
[Agent Plugins](https://agent-plugins.org/specification), and Grok Build's bundled
user guide (`~/.grok/docs/user-guide/10-hooks.md`).

## Verification

- `python3 -m unittest discover -s tests` covers two things:
  - The package guard: tampered, unpinned, default-path, executable and
    network-reaching hooks are all rejected.
  - The script itself, run under the system `sh` (dash on the Ubuntu CI runner):
    output, opt-outs, the `connected` gate, attended and unattended sessions,
    once-per-session, the loop guard, the heuristics against the real transcript
    fixture and reordered keys, and fail-open inputs, including a read-only data
    directory.
- `claude plugin validate ./plugins/ditto` reads `hooks/claude-hooks.json` and checks
  its event names.
- **Live check (2026-11-13)** with Claude Code 2.1.308, using a local test double
  for the Ditto server (a stdio MCP server named `ditto` with one
  `search_memories` tool):
  - Headless, no `connected` file yet: SessionStart printed nothing. `PostToolUse`
    fired on `mcp__ditto__search_memories` and created the file. Stop stayed
    silent, because the session was unattended.
  - Headless with `DITTO_HOOKS_STOP=1`: SessionStart added the context, and Stop
    asked once. The agent answered in one line, and the second Stop was silent.
  - Interactive terminal (`CLAUDE_CODE_SESSION_ATTENDED=1`): Stop asked once
    through `additionalContext`, with no "error" label.
- **Live check (2026-11-10)**, before the `connected` gate, using
  `claude -p --plugin-dir`:
  - SessionStart added the context in 22 ms.
  - A session that wrote a file got one Stop check. The agent replied with one line
    and the second Stop stayed silent.
  - A session with one shell command got no check.
  - `/compact` on a resumed session ran SessionStart `compact` after the boundary,
    and the PreCompact text reached the compaction.

  Neither check connected a real Ditto account, so they show that the hooks fire
  and stay quiet as designed. They do not show an authenticated save.

Windows: Claude Code runs hook commands in Git Bash. Without Git Bash it uses
PowerShell, where `sh` is missing. The hooks then fail and Claude Code ignores
them; the skills still work.
