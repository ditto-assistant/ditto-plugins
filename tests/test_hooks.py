"""Lifecycle hooks: the package guard around them and the script's behaviour.

The script runs under the system `sh` (dash on the Ubuntu CI runner) exactly as
the host runs it, with the event's JSON on stdin.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package", ROOT / "scripts/validate_package.py")
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)

PLUGIN = "plugins/ditto"
FIXTURES = ROOT / "tests/fixtures"
SCRIPT = ROOT / PLUGIN / "hooks/ditto-hook.sh"
CONFIG = f"{PLUGIN}/hooks/claude-hooks.json"


class HookPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for folder in ("plugins", ".claude-plugin", ".cursor-plugin", ".grok-plugin", ".agents", ".github/plugin", ".kimi-plugin"):
            shutil.copytree(ROOT / folder, self.root / folder)
        (self.root / "scripts").mkdir()
        shutil.copy(ROOT / package.HOOK_ALLOWLIST, self.root / package.HOOK_ALLOWLIST)

    def edit(self, relative, change):
        f = self.root / relative
        data = json.loads(f.read_text())
        change(data)
        f.write_text(json.dumps(data))

    def pin(self, relative):
        """Re-pin a file's hash, as a reviewed PR would, so only the other checks apply."""
        self.edit(package.HOOK_ALLOWLIST, lambda d: d.__setitem__(relative, hashlib.sha256((self.root / relative).read_bytes()).hexdigest()))

    def edit_config(self, change):
        self.edit(CONFIG, change)
        self.pin(CONFIG)

    def test_release_hooks_are_pinned(self):
        self.assertGreater(package.validate(self.root), 0)
        self.assertEqual(sorted(package.hook_allowlist(ROOT)), [CONFIG, f"{PLUGIN}/hooks/ditto-hook.sh"])

    def test_changed_or_unlisted_hook_files_are_rejected(self):
        cases = (
            ("prepended code", lambda: SCRIPT.read_bytes().replace(b"#!/bin/sh\n", b"#!/bin/sh\ntouch ~/.x\n", 1), "ditto-hook.sh"),
            ("new hook file", lambda: b"echo hi\n", "extra.sh"),
        )
        for label, content, name in cases:
            with self.subTest(label):
                self.setUp()
                (self.root / PLUGIN / "hooks" / name).write_bytes(content())
                with self.assertRaisesRegex(ValueError, "Unlisted or changed hook file"):
                    package.validate(self.root)
        for relative in (f"{PLUGIN}/README.md", package.HOOK_ALLOWLIST, f"{PLUGIN}/hooks/../README.md"):
            with self.subTest(relative=relative):
                self.setUp()
                self.edit(package.HOOK_ALLOWLIST, lambda d: d.__setitem__(relative, "0" * 64))
                with self.assertRaisesRegex(ValueError, "must map plugins/<name>/hooks/<file>"):
                    package.validate(self.root)
        self.setUp()
        self.edit(package.HOOK_ALLOWLIST, lambda d: d.__setitem__(f"{PLUGIN}/hooks/gone.sh", "0" * 64))
        with self.assertRaisesRegex(ValueError, "lists a missing file"):
            package.validate(self.root)

    def test_pinned_hooks_still_cannot_reach_the_network(self):
        for line in (b"curl -s https://example.com\n", b"node -e 1\n", b"exec 3<>/dev/tcp/example.com/80\n"):
            with self.subTest(line=line):
                self.setUp()
                script = self.root / PLUGIN / "hooks/ditto-hook.sh"
                script.write_bytes(script.read_bytes().replace(b"exit 0\n", line + b"exit 0\n", 1))
                self.pin(f"{PLUGIN}/hooks/ditto-hook.sh")
                with self.assertRaisesRegex(ValueError, "network tool"):
                    package.validate(self.root)

    def test_default_hooks_file_is_rejected_even_when_pinned(self):
        relative = f"{PLUGIN}/hooks/hooks.json"
        shutil.copy(self.root / CONFIG, self.root / relative)
        self.pin(relative)
        with self.assertRaisesRegex(ValueError, "auto-discovered"):
            package.validate(self.root)

    def test_plugin_root_hooks_json_is_not_a_release_file(self):
        # Copilot CLI and Antigravity read <plugin>/hooks.json by themselves.
        shutil.copy(self.root / CONFIG, self.root / PLUGIN / "hooks.json")
        with self.assertRaisesRegex(ValueError, "Unexpected release file"):
            package.validate(self.root)

    def test_executable_release_files_are_rejected(self):
        (self.root / PLUGIN / "hooks/ditto-hook.sh").chmod(0o755)
        with self.assertRaisesRegex(ValueError, "Executable release file"):
            package.validate(self.root)

    def test_only_the_claude_manifest_wires_hooks(self):
        cases = (
            (".cursor-plugin/plugin.json", "./hooks/claude-hooks.json"),
            (".codex-plugin/plugin.json", "./hooks/claude-hooks.json"),
            (".github/plugin/plugin.json", "./hooks/claude-hooks.json"),
            (".grok-plugin/plugin.json", "./hooks/claude-hooks.json"),
            (".claude-plugin/plugin.json", "./hooks/other.json"),
            (".claude-plugin/plugin.json", {"Stop": []}),
            (".cursor-plugin/plugin.json", None),
            (".claude-plugin/plugin.json", None),
        )
        for manifest, value in cases:
            with self.subTest(manifest=manifest, value=value):
                self.setUp()
                self.edit(f"{PLUGIN}/{manifest}", lambda d: d.__setitem__("hooks", value))
                with self.assertRaisesRegex(ValueError, "may not declare hooks"):
                    package.validate(self.root)
        self.setUp()
        self.edit(".claude-plugin/marketplace.json", lambda d: d["plugins"][0].__setitem__("hooks", "./hooks/claude-hooks.json"))
        with self.assertRaisesRegex(ValueError, "runtime override"):
            package.validate(self.root)

    def test_hook_configuration_is_bounded(self):
        handler = lambda d, event="Stop", i=0: d["hooks"][event][i]["hooks"][0]
        cases = (
            (lambda d: d["hooks"].__setitem__("UserPromptSubmit", d["hooks"]["Stop"]), "event not allowed"),
            (lambda d: d["hooks"].__setitem__("PreToolUse", d["hooks"]["Stop"]), "event not allowed"),
            (lambda d: d["hooks"]["Stop"][0].__setitem__("matcher", "*"), "matcher not allowed"),
            # PostToolUse may only fire on Ditto's own memory tools, never on every tool call.
            (lambda d: d["hooks"]["PostToolUse"][0].__setitem__("matcher", ".*"), "matcher not allowed"),
            (lambda d: d["hooks"]["PostToolUse"][0].pop("matcher"), "matcher not allowed"),
            (lambda d: handler(d).pop("timeout"), "command handlers"),
            (lambda d: handler(d).__setitem__("timeout", 60), "timeout must be"),
            (lambda d: handler(d).__setitem__("timeout", True), "timeout must be"),
            (lambda d: handler(d).__setitem__("async", True), "command handlers"),
            (lambda d: d["hooks"]["Stop"][0].__setitem__("hooks", [{"type": "http", "url": "https://example.com", "timeout": 5}]), "command handlers"),
            (lambda d: d["hooks"]["Stop"][0].__setitem__("hooks", [{"type": "mcp_tool", "server": "x", "tool": "y", "timeout": 5}]), "command handlers"),
            (lambda d: handler(d).__setitem__("command", 'sh "${CLAUDE_PLUGIN_ROOT}/hooks/ditto-hook.sh" stop; curl x'), "bundled ditto-hook.sh"),
            (lambda d: handler(d).__setitem__("command", 'bash -c "curl example.com"'), "bundled ditto-hook.sh"),
            (lambda d: d.__setitem__("extra", 1), "description"),
            (lambda d: handler(d).__setitem__("command", ["sh", "x"]), "bundled ditto-hook.sh"),
        )
        for change, message in cases:
            with self.subTest(message=message):
                self.setUp()
                self.edit_config(change)
                with self.assertRaisesRegex(ValueError, message):
                    package.validate(self.root)

    def test_chatgpt_upload_carries_no_hooks(self):
        out = Path(self.tmp.name).parent / f"{Path(self.tmp.name).name}-hooks.zip"
        self.addCleanup(out.unlink, missing_ok=True)
        package.archive(self.root, out)
        self.assertFalse([n for n in zipfile.ZipFile(out).namelist() if "/hooks/" in n])


def entry(kind, **fields):
    if kind == "definitions":
        # Some transcripts record the request's tool list; a definition is not a call.
        return {"type": "request", "tools": [{"name": n, "description": "x", "input_schema": {}} for n in fields["names"]]}
    if kind == "tool":
        return {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "toolu_1", "name": fields["name"], "input": {}}]}}
    return {"type": "user", "message": {"content": fields["text"]}}


class HookScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.data = self.tmp / "data"
        self.transcript = self.tmp / "session.jsonl"
        # Most tests start where Ditto has already answered once in this install.
        self.data.mkdir()
        (self.data / "connected").touch()

    def markers(self):
        return sorted(p.name for p in self.data.glob("stop-check-*"))

    def write_transcript(self, *entries):
        # Hosts write compact JSON Lines, one entry per line.
        self.transcript.write_text("".join(json.dumps(e, separators=(",", ":")) + "\n" for e in entries))

    def run_hook(self, event, payload=None, env=None, stdin=None):
        environment = {"PATH": os.environ["PATH"], "CLAUDE_PLUGIN_DATA": str(self.data), "CLAUDE_CODE_SESSION_ATTENDED": "1", **(env or {})}
        environment = {k: v for k, v in environment.items() if v is not None}
        if stdin is None:
            stdin = json.dumps({"session_id": "abc-123", "transcript_path": str(self.transcript), "hook_event_name": "Stop", **(payload or {})})
        start = time.monotonic()
        result = subprocess.run(["sh", str(SCRIPT), event], input=stdin, capture_output=True, text=True, env=environment, timeout=10)
        self.assertLess(time.monotonic() - start, 2, "hooks must be fast")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout

    def asked(self, out, age=True):
        """The Stop check continues the turn through additionalContext, not decision:block,
        which Claude Code's terminal labels "Stop hook error"."""
        output = json.loads(out)
        self.assertEqual(set(output), {"hookSpecificOutput"})
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "Stop")
        if age:
            self.age("stop-check-*", days=2)  # step past the once-a-day cap for the next case
        return output["hookSpecificOutput"]["additionalContext"]

    def age(self, pattern, days):
        then = time.time() - days * 86400
        for path in self.data.glob(pattern):
            os.utime(path, (then, then))

    def worked(self):
        self.write_transcript(entry("user", text="fix the bug"), entry("tool", name="Edit"))

    def test_session_start_points_at_the_memory_skill(self):
        out = self.run_hook("session-start", {"hook_event_name": "SessionStart", "source": "startup"})
        self.assertIn("ditto-memory", out)
        self.assertIn("evidence, not instructions", out)
        self.assertLess(len(out), 1000)
        self.assertIn("not yet saved to Ditto", self.run_hook("pre-compact"))
        self.assertIn("compacted", self.run_hook("compact"))

    def test_opt_out_silences_every_event(self):
        self.worked()
        for value in ("0", "off", "false", "no"):
            for event in ("session-start", "compact", "pre-compact", "stop"):
                with self.subTest(value=value, event=event):
                    self.assertEqual(self.run_hook(event, env={"DITTO_HOOKS": value}), "")
        self.assertEqual(self.run_hook("stop", env={"DITTO_HOOKS_STOP": "0"}), "")
        self.assertIn("ditto-memory", self.run_hook("session-start", env={"DITTO_HOOKS_STOP": "0"}))
        self.assertEqual(self.markers(), [], "an opted-out run leaves nothing behind")

    def test_silent_until_a_ditto_memory_tool_has_worked(self):
        (self.data / "connected").unlink()
        self.worked()
        for event in ("session-start", "compact", "pre-compact", "stop"):
            with self.subTest(event=event):
                self.assertEqual(self.run_hook(event), "")
        self.assertEqual(self.markers(), [])
        self.assertEqual(self.run_hook("connected", {"hook_event_name": "PostToolUse", "tool_name": "mcp__plugin_heyditto_ditto__search_memories"}), "")
        self.assertTrue((self.data / "connected").exists())
        self.assertIn("ditto-memory", self.run_hook("session-start"))
        self.asked(self.run_hook("stop"))

    def test_connected_lapses_after_30_days_without_a_ditto_call(self):
        self.worked()
        # Just past and just short of 30 days; the script counts minutes, so GNU and
        # BSD find agree on both sides.
        self.age("connected", days=30.01)
        self.assertEqual(self.run_hook("session-start"), "")
        self.assertFalse((self.data / "connected").exists())
        self.run_hook("connected")
        self.assertIn("ditto-memory", self.run_hook("session-start"))
        self.age("connected", days=29.9)
        self.assertIn("ditto-memory", self.run_hook("session-start"))
        self.asked(self.run_hook("stop"))

    def test_error_results_do_not_mark_connected(self):
        (self.data / "connected").unlink()
        for response in ({"isError": True, "content": []}, {"is_error": True}):
            with self.subTest(response=response):
                self.assertEqual(self.run_hook("connected", {"hook_event_name": "PostToolUse", "tool_response": response}), "")
                self.assertFalse((self.data / "connected").exists())
        self.run_hook("connected", {"hook_event_name": "PostToolUse", "tool_response": {"isError": False, "content": []}})
        self.assertTrue((self.data / "connected").exists())

    def test_connected_creates_the_data_dir_and_fails_open(self):
        shutil.rmtree(self.data)
        self.assertEqual(self.run_hook("connected"), "")
        self.assertTrue((self.data / "connected").exists())
        for env in ({"CLAUDE_PLUGIN_DATA": ""}, {"CLAUDE_PLUGIN_DATA": str(self.transcript / "x")}, {"DITTO_HOOKS": "0", "CLAUDE_PLUGIN_DATA": str(self.tmp / "other")}):
            with self.subTest(env=env):
                self.transcript.write_text("")
                self.assertEqual(self.run_hook("connected", env=env), "")
        self.assertFalse((self.tmp / "other").exists(), "opted out: no marker")

    def test_stop_skips_unattended_sessions_unless_asked(self):
        self.worked()
        quiet = {
            "claude -p": {"CLAUDE_CODE_SESSION_ATTENDED": "0", "CLAUDE_CODE_ENTRYPOINT": "sdk-cli"},
            "older host, sdk entrypoint": {"CLAUDE_CODE_SESSION_ATTENDED": None, "CLAUDE_CODE_ENTRYPOINT": "sdk-ts"},
        }
        for label, env in quiet.items():
            with self.subTest(label):
                self.assertEqual(self.run_hook("stop", {"session_id": label.replace(" ", "-")}, env=env), "")
                self.assertIn("ditto-memory", self.run_hook("session-start", env=env), "recall still runs at automation start")
        self.assertEqual(self.markers(), [])
        forced = {"CLAUDE_CODE_SESSION_ATTENDED": "0", "DITTO_HOOKS_STOP": "1"}
        self.asked(self.run_hook("stop", {"session_id": "forced"}, env=forced))
        attended = {"CLAUDE_CODE_SESSION_ATTENDED": "1", "CLAUDE_CODE_ENTRYPOINT": "sdk-cli"}
        self.asked(self.run_hook("stop", {"session_id": "attended"}, env=attended))
        legacy = {"CLAUDE_CODE_SESSION_ATTENDED": None, "CLAUDE_CODE_ENTRYPOINT": "cli"}
        self.asked(self.run_hook("stop", {"session_id": "legacy"}, env=legacy))

    def test_stop_asks_once_per_session_after_real_work(self):
        self.worked()
        reason = self.asked(self.run_hook("stop"), age=False)
        self.assertIn("ditto-memory", reason)
        self.assertIn("authorized", reason)
        self.assertIn("not already declined", reason)
        self.assertEqual(self.run_hook("stop"), "", "second stop in the same session")
        self.assertEqual(self.run_hook("stop", {"session_id": "same-day"}), "", "at most once a day")
        self.age("stop-check-*", days=2)
        self.assertEqual(self.run_hook("stop"), "", "the session marker outlives the daily cap")
        self.asked(self.run_hook("stop", {"session_id": "next-day"}))

    def test_stop_never_loops_on_its_own_continuation(self):
        self.worked()
        self.assertEqual(self.run_hook("stop", {"stop_hook_active": True}), "")
        self.assertEqual(self.markers(), [])

    def test_stop_stays_quiet_without_work_or_after_a_save(self):
        cases = {
            "chat only": [entry("user", text="hi")],
            "a few reads": [entry("tool", name="Read")] * 9,
            "already saved": [entry("tool", name="Edit"), entry("tool", name="mcp__plugin_heyditto_ditto__save_memory")],
            "already updated": [entry("tool", name="Write"), entry("tool", name="mcp__ditto__update_memory")],
            "edit mentioned in text": [entry("user", text='{"name":"Edit"}')],
            "tools only defined": [entry("definitions", names=["Edit", "Write", "mcp__plugin_heyditto_ditto__save_memory"])],
        }
        for label, entries in cases.items():
            with self.subTest(label):
                self.write_transcript(*entries)
                self.assertEqual(self.run_hook("stop", {"session_id": label.replace(" ", "-")}), "")
        self.write_transcript(*[entry("tool", name="Bash")] * 10)
        self.asked(self.run_hook("stop", {"session_id": "ten-calls"}))
        # A defined-but-unused save tool must not hide real work.
        self.write_transcript(entry("definitions", names=["mcp__plugin_heyditto_ditto__save_memory"]), entry("tool", name="Edit"))
        self.asked(self.run_hook("stop", {"session_id": "save-defined"}))

    def test_stop_reads_a_real_claude_code_transcript(self):
        # A Write call as Claude Code 2.1.308 recorded it, keys in their recorded order,
        # identifying values replaced. If a Claude Code release changes this shape and
        # the check stops firing, this is the test that should be updated (docs/hooks.md).
        line = (FIXTURES / "claude-code-2.1.308-write.jsonl").read_text()
        self.assertIn('"type":"tool_use","id":"toolu_fixture","name":"Write","input":', line)
        self.transcript.write_text(line)
        self.asked(self.run_hook("stop"))

    def test_stop_tolerates_reordered_tool_use_keys(self):
        for block in ({"name": "Edit", "input": {}, "type": "tool_use", "id": "toolu_1"},
                      {"id": "toolu_1", "type": "tool_use", "name": "Edit", "input": {}}):
            with self.subTest(order=list(block)):
                self.transcript.write_text(json.dumps({"type": "assistant", "message": {"content": [block]}}, separators=(",", ":")) + "\n")
                self.asked(self.run_hook("stop", {"session_id": "-".join(block)}))

    def test_stop_fails_open(self):
        self.worked()
        cases = {
            "malformed input": dict(stdin="not json"),
            "empty input": dict(stdin=""),
            "no plugin data dir": dict(env={"CLAUDE_PLUGIN_DATA": ""}),
            "missing transcript": dict(payload={"transcript_path": str(self.tmp / "missing.jsonl")}),
            "unsafe session id": dict(payload={"session_id": "../../"}),
            "unwritable data dir": dict(env={"CLAUDE_PLUGIN_DATA": str(self.transcript)}),
            "unknown event": dict(),
        }
        for label, kwargs in cases.items():
            with self.subTest(label):
                self.assertEqual(self.run_hook("bogus" if label == "unknown event" else "stop", **kwargs), "")

    def test_ages_are_counted_in_minutes(self):
        # Day-granular -mtime rounds differently on GNU (down) and BSD (documented as up).
        self.assertNotIn("-mtime", SCRIPT.read_text())
        self.worked()
        self.asked(self.run_hook("stop", {"session_id": "first"}), age=False)
        self.age("stop-check-*", days=0.99)
        self.assertEqual(self.run_hook("stop", {"session_id": "under-a-day"}), "")
        self.age("stop-check-*", days=1.01)
        self.asked(self.run_hook("stop", {"session_id": "over-a-day"}))

    def test_marker_is_written_after_the_reminder(self):
        script = SCRIPT.read_text()
        reminder = script.index('"additionalContext":"Ditto end-of-task check')
        self.assertGreater(script.index('touch "$marker"'), reminder)
        self.assertLess(script.index('[ -w "$data" ] || exit 0'), reminder)

    @unittest.skipIf(os.geteuid() == 0, "root ignores directory permissions")
    def test_read_only_data_dir_fails_open_quietly(self):
        self.worked()
        self.data.chmod(0o500)
        self.addCleanup(self.data.chmod, 0o700)
        self.assertEqual(self.run_hook("stop"), "")
        self.assertEqual(self.run_hook("connected"), "")

    def test_stop_reads_escaped_paths(self):
        weird = self.tmp / 'dir with "quote" and \\ slash'
        weird.mkdir()
        self.transcript = weird / "session.jsonl"
        self.worked()
        # A quoted path is not parsed (fail open); a backslash path is unescaped.
        self.assertEqual(self.run_hook("stop"), "")
        for name in ("back\\slash", "trailing\\"):
            with self.subTest(name=name):
                folder = self.tmp / name
                folder.mkdir()
                self.transcript = folder / "session.jsonl"
                self.worked()
                self.asked(self.run_hook("stop", {"session_id": "s-" + str(len(name))}))


if __name__ == "__main__":
    unittest.main()
