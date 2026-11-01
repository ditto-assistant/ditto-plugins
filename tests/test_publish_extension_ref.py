"""The Gemini extension branch carries plugins/ditto as its root and only fast-forwards."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/publish_extension_ref.py"
# Empty global/system config, so a developer's signing, hooks or templates
# cannot reach these throwaway repositories.
ENV = {**os.environ, "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@example.invalid",
       "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@example.invalid",
       "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}


class PublishExtensionRefTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.remote = base / "remote.git"
        self.work = base / "work"
        self.git(base, "init", "-q", "--bare", str(self.remote))
        self.git(base, "init", "-q", "-b", "main", str(self.work))
        self.git(self.work, "remote", "add", "origin", str(self.remote))
        self.write("plugins/ditto/gemini-extension.json", '{"name": "ditto", "version": "1.0.0"}\n')
        self.write("plugins/ditto/skills/a/SKILL.md", "---\nname: a\ndescription: A.\n---\n")
        self.write("README.md", "root only\n")
        self.commit("one")

    def git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, env=ENV, check=True, capture_output=True, text=True).stdout.strip()

    def write(self, relative, text):
        path = self.work / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, message):
        self.git(self.work, "add", "-A")
        self.git(self.work, "commit", "-qm", message)

    def publish(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.work, env=ENV, capture_output=True, text=True)

    def remote_tree(self, ref="gemini-extension"):
        return self.git(self.remote, "ls-tree", "-r", "--name-only", ref).splitlines()

    def test_branch_root_is_the_plugin_folder_and_republishing_is_a_fast_forward(self):
        self.assertEqual(self.publish().returncode, 0)
        self.assertEqual(self.remote_tree(), ["gemini-extension.json", "skills/a/SKILL.md"])
        first = self.git(self.remote, "rev-parse", "gemini-extension")
        unchanged = self.publish()
        self.assertIn("nothing to publish", unchanged.stdout)
        self.assertEqual(self.git(self.remote, "rev-parse", "gemini-extension"), first)
        self.write("README.md", "root edits do not republish\n")
        self.commit("root")
        self.assertIn("nothing to publish", self.publish().stdout)
        self.write("plugins/ditto/gemini-extension.json", '{"name": "ditto", "version": "1.0.1"}\n')
        self.commit("bump")
        self.assertEqual(self.publish().returncode, 0)
        second = self.git(self.remote, "rev-parse", "gemini-extension")
        self.assertEqual(self.git(self.remote, "rev-parse", f"{second}^"), first)
        self.assertIn("1.0.1", self.git(self.remote, "show", "gemini-extension:gemini-extension.json"))

    def test_dry_run_pushes_nothing(self):
        result = self.publish("--dry-run")
        self.assertIn("dry run", result.stdout)
        self.assertEqual(self.git(self.remote, "for-each-ref", "refs/heads"), "")

    def test_missing_manifest_is_refused(self):
        self.git(self.work, "rm", "-q", "plugins/ditto/gemini-extension.json")
        self.commit("drop")
        result = self.publish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("gemini-extension.json is missing", result.stderr)
        self.assertEqual(self.git(self.remote, "for-each-ref", "refs/heads"), "")

    def test_a_branch_moved_by_someone_else_is_not_overwritten(self):
        self.assertEqual(self.publish().returncode, 0)
        other = Path(self.tmp.name) / "other"
        self.git(Path(self.tmp.name), "clone", "-q", "--branch", "gemini-extension", str(self.remote), str(other))
        (other / "extra.md").write_text("x\n")
        self.git(other, "add", "-A")
        self.git(other, "commit", "-qm", "manual")
        self.git(other, "push", "-q", "origin", "gemini-extension")
        moved = self.git(self.remote, "rev-parse", "gemini-extension")
        self.write("plugins/ditto/skills/a/SKILL.md", "---\nname: a\ndescription: A, revised.\n---\n")
        self.commit("edit")
        # The fetched head is the parent, so the push is a fast-forward over the manual commit.
        self.assertEqual(self.publish().returncode, 0)
        self.assertEqual(self.git(self.remote, "rev-parse", "gemini-extension^"), moved)
        self.assertNotIn("extra.md", self.remote_tree())


if __name__ == "__main__":
    unittest.main()
