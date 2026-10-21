"""Real disposable Git repository snapshots; no model calls."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import engineering


class EngineeringEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        self.root.mkdir()
        self.git("init", "-q")
        (self.root / "source.py").write_text("value = 1\n")
        (self.root / "other.py").write_text("unchanged = True\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "baseline")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True).stdout

    def test_dirty_baseline_and_exact_attempt_diff(self):
        (self.root / "source.py").write_text("value = 2\n")
        before = engineering.snapshot(self.root, ["source.py"])
        (self.root / "source.py").write_text("value = 3\n")
        after = engineering.snapshot(self.root, ["source.py"])
        change = engineering.compare(before, after, ["source.py"])
        self.assertEqual(change["changed_paths"], ["source.py"])
        self.assertEqual(change["violations"], [])
        self.assertIn("-value = 2\n+value = 3", change["patch"])
        self.assertNotIn("value = 1", change["patch"])
        self.assertEqual(before["contents"]["source.py"], "value = 2\n")

    def test_new_deleted_and_out_of_scope_files(self):
        scope = ["source.py", "new.py"]
        before = engineering.snapshot(self.root, scope)
        self.assertIsNone(before["files"]["new.py"])
        (self.root / "source.py").unlink()
        (self.root / "new.py").write_text("new = True\n")
        (self.root / "other.py").write_text("changed = True\n")
        after = engineering.snapshot(self.root, scope)
        change = engineering.compare(before, after, scope)
        self.assertEqual(change["changed_paths"], ["new.py", "other.py", "source.py"])
        self.assertEqual(change["violations"], ["other.py"])
        self.assertIn("+new = True", change["patch"])
        self.assertIn("-value = 1", change["patch"])
        self.assertIn("other.py", change["patch_omissions"])

    def test_snapshot_is_deterministic_and_has_no_git_side_effects(self):
        before_index = (self.root / ".git/index").read_bytes()
        before = engineering.snapshot(self.root, ["source.py"])
        os.utime(self.root / "source.py", None)
        self.assertEqual(before, engineering.snapshot(self.root, ["source.py"]))
        self.assertEqual(before_index, (self.root / ".git/index").read_bytes())

    def test_scope_paths_and_directory_boundaries(self):
        (self.root / "src").mkdir()
        self.assertEqual(engineering.validate_scope(self.root, ["src", "new/", "source.py", "src/"]),
                         ["new/", "source.py", "src/"])
        self.assertTrue(engineering.owns("src/a.py", ["src/"]))
        self.assertFalse(engineering.owns("src-other/a.py", ["src/"]))
        self.assertFalse(engineering.owns("source.py.backup", ["source.py"]))
        for value in ("../escape", "/absolute", ".", ".git/config", "src/../../escape", "src\\escape"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                engineering.validate_scope(self.root, [value])

    def test_symlink_entries_and_scopes_are_refused(self):
        outside = self.root.parent / "outside"
        outside.write_text("private one")
        (self.root / "link").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink repository entries"):
            engineering.snapshot(self.root)
        with self.assertRaisesRegex(ValueError, "symlink"):
            engineering.validate_scope(self.root, ["link"])
        (self.root / "directory-link").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            engineering.validate_scope(self.root, ["directory-link/new.py"])

    def test_digest_is_scope_independent_including_absent_owned_files(self):
        before = engineering.snapshot(self.root, ["source.py", "uncreated.py"])
        reviewed = engineering.snapshot(self.root, [])
        self.assertEqual(before["digest"], reviewed["digest"])
        self.assertIsNone(before["files"]["uncreated.py"])
        self.assertNotIn("uncreated.py", reviewed["files"])

    def test_symlink_root_and_replaced_tracked_parent_are_refused(self):
        alias = self.root.parent / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            engineering.snapshot(alias)
        (self.root / "src").mkdir()
        (self.root / "src/a.py").write_text("a = 1")
        self.git("add", "src/a.py")
        (self.root / "src/a.py").unlink()
        (self.root / "src").rmdir()
        (self.root / "src").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink|safely inspect"):
            engineering.snapshot(self.root)

    def test_readonly_detects_changes_and_mode_changes(self):
        before = engineering.snapshot(self.root)
        (self.root / "source.py").chmod(0o755)
        after = engineering.snapshot(self.root)
        change = engineering.compare(before, after, [])
        self.assertEqual(change["changed_paths"], ["source.py"])
        self.assertEqual(change["violations"], ["source.py"])
        self.assertNotEqual(before["digest"], after["digest"])
        self.assertFalse(change["patch_complete"])

    def test_ignored_files_are_excluded_unless_explicitly_owned(self):
        (self.root / ".gitignore").write_text("ignored\n")
        (self.root / "ignored").write_text("output")
        self.assertNotIn("ignored", engineering.snapshot(self.root)["files"])
        self.assertIn("ignored", engineering.snapshot(self.root, ["ignored"])["files"])

    def test_text_omission_is_explicit_and_hash_remains(self):
        before = engineering.snapshot(self.root, ["source.py"])
        (self.root / "source.py").write_text("long text")
        with patch.object(engineering, "MAX_TEXT_BYTES", 3):
            after = engineering.snapshot(self.root, ["source.py"])
        self.assertIn("source.py", after["files"])
        self.assertNotIn("source.py", after["contents"])
        self.assertIn("source.py", after["content_omissions"])
        change = engineering.compare(before, after, ["source.py"])
        self.assertFalse(change["patch_complete"])
        self.assertEqual(change["patch_omissions"], ["source.py"])

    def test_limits_and_linked_worktree_and_unborn_repository(self):
        with patch.object(engineering, "MAX_FILES", 1), self.assertRaisesRegex(ValueError, "audited files"):
            engineering.snapshot(self.root)
        with patch.object(engineering, "MAX_FILE_BYTES", 1), self.assertRaisesRegex(ValueError, "file exceeds"):
            engineering.snapshot(self.root)
        linked = self.root.parent / "linked"
        self.git("worktree", "add", "--detach", str(linked))
        with self.assertRaisesRegex(ValueError, "linked worktrees"):
            engineering.snapshot(linked)
        unborn = self.root.parent / "unborn"
        unborn.mkdir()
        subprocess.run(["git", "-C", str(unborn), "init", "-q"], check=True)
        self.assertIsNone(engineering.snapshot(unborn)["revision"])

    def test_commits_are_visible_and_different_roots_cannot_compare(self):
        before = engineering.snapshot(self.root, ["source.py"])
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "-qm", "new revision")
        after = engineering.snapshot(self.root, ["source.py"])
        self.assertEqual(engineering.compare(before, after, ["source.py"])["violations"], [".git/HEAD"])
        with self.assertRaisesRegex(ValueError, "different repository"):
            engineering.compare(before, dict(after, root="/different"), [])

    def test_git_timeout_is_a_bounded_evidence_error(self):
        with patch.object(engineering.subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 5)):
            with self.assertRaisesRegex(ValueError, "inspection could not complete"):
                engineering.snapshot(self.root)

    def test_private_copy_preserves_dirty_bytes_and_source_without_hardlinks(self):
        (self.root / "source.py").write_text("value = 2\n")
        (self.root / "source.py").chmod(0o640)
        (self.root / "untracked.py").write_text("new = True\n")
        index = (self.root / ".git/index").read_bytes()
        original = engineering.snapshot(self.root, ["source.py"])
        destination = self.root.parent / "workspaces/task"
        origin = engineering.copy_repository(self.root, destination, ["source.py"])
        self.assertEqual(origin, original)
        self.assertEqual(engineering.snapshot(self.root, ["source.py"]), original)
        self.assertEqual((self.root / ".git/index").read_bytes(), index)
        self.assertNotEqual((destination / "source.py").stat().st_ino, (self.root / "source.py").stat().st_ino)
        self.assertEqual((destination / "source.py").stat().st_mode & 0o777, 0o640)
        self.assertEqual((destination / "source.py").read_text(), "value = 2\n")
        self.assertEqual((destination / "untracked.py").read_text(), "new = True\n")
        self.assertIsNone(engineering.snapshot(destination)["revision"])
        (destination / "source.py").write_text("value = 3\n")
        self.assertEqual((self.root / "source.py").read_text(), "value = 2\n")

    def test_private_copy_excludes_caches_and_retains_tracked_ignored_files(self):
        (self.root / ".gitignore").write_text("cache/\ntracked-output\nexplicit-output\n")
        (self.root / "cache").mkdir()
        (self.root / "cache/generated").write_text("not copied")
        (self.root / "tracked-output").write_text("tracked output")
        (self.root / "explicit-output").write_text("explicit output")
        self.git("add", "--force", "tracked-output")
        destination = self.root.parent / "copy"
        engineering.copy_repository(self.root, destination, ["explicit-output"])
        self.assertFalse((destination / "cache").exists())
        copied = engineering.snapshot(destination)
        self.assertIn("tracked-output", copied["files"])
        self.assertIn("explicit-output", copied["files"])

    def test_private_copy_refuses_existing_source_relative_and_symlink_destinations(self):
        destination = self.root.parent / "existing"
        destination.mkdir()
        (destination / "sentinel").write_text("keep")
        with self.assertRaisesRegex(ValueError, "already exists"):
            engineering.copy_repository(self.root, destination)
        self.assertEqual((destination / "sentinel").read_text(), "keep")
        for target in (self.root / "copy", self.root, self.root.parent):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "outside"):
                engineering.copy_repository(self.root, target)
        alias = self.root.parent / "alias"
        alias.symlink_to(destination, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            engineering.copy_repository(self.root, alias / "new")
        (self.root / "link").symlink_to(self.root / "source.py")
        with self.assertRaisesRegex(ValueError, "symlink"):
            engineering.copy_repository(self.root, self.root.parent / "new")

    def test_private_copy_detects_source_changes_and_cleans_its_stage(self):
        actual_git = engineering._git
        def changing_git(root, *args, **kwargs):
            result = actual_git(root, *args, **kwargs)
            if args and args[0] == "init":
                (self.root / "source.py").write_text("changed during copy\n")
            return result
        destination = self.root.parent / "copy"
        with patch.object(engineering, "_git", side_effect=changing_git):
            with self.assertRaisesRegex(ValueError, "source changed"):
                engineering.copy_repository(self.root, destination)
        self.assertFalse(destination.exists())
        self.assertEqual(list(self.root.parent.glob(".engineering-copy-*")), [])

    def test_private_copy_does_not_replace_a_racing_destination(self):
        actual_snapshot = engineering.snapshot
        destination = self.root.parent / "copy"
        def racing_snapshot(root, scope=()):
            result = actual_snapshot(root, scope)
            if Path(root).name.startswith(".engineering-copy-"):
                destination.mkdir()
                (destination / "sentinel").write_text("keep")
            return result
        with patch.object(engineering, "snapshot", side_effect=racing_snapshot):
            with self.assertRaisesRegex(ValueError, "without overwriting"):
                engineering.copy_repository(self.root, destination)
        self.assertEqual((destination / "sentinel").read_text(), "keep")
        self.assertEqual(list(self.root.parent.glob(".engineering-copy-*")), [])

    def test_private_copy_does_not_run_configured_clean_filter(self):
        (self.root / ".gitattributes").write_text("*.py filter=fixture\n")
        home = self.root.parent / "home"
        home.mkdir()
        sentinel = self.root.parent / "filter-executed"
        (home / ".gitconfig").write_text('[filter "fixture"]\n\tclean = "touch ' + str(sentinel) + ' && cat"\n')
        with patch.dict(os.environ, {"HOME": str(home)}):
            engineering.copy_repository(self.root, self.root.parent / "copy")
        self.assertFalse(sentinel.exists())

    def test_explicit_directory_audit_captures_ignored_wrappers_and_outputs(self):
        (self.root / ".gitignore").write_text("scratch/\n")
        before = engineering.snapshot(self.root, ["scratch/"])
        (self.root / "scratch/nested").mkdir(parents=True)
        (self.root / "scratch/wrapper.py").write_text("print('observed')\n")
        (self.root / "scratch/nested/output.bin").write_bytes(b"\xff\x00\x01")
        after = engineering.snapshot(self.root, ["scratch/"])
        self.assertIn("scratch/wrapper.py", after["contents"])
        self.assertIn("scratch/nested/output.bin", after["files"])
        self.assertIn("scratch/nested/output.bin", after["content_omissions"])
        result = engineering.compare(before, after, ["scratch/"])
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["changed_paths"], ["scratch/nested/output.bin", "scratch/wrapper.py"])
        self.assertNotEqual(engineering.snapshot(self.root)["digest"], after["digest"])
        review = engineering.snapshot(self.root, ["scratch/"])
        self.assertEqual(review["digest"], after["digest"])
        (self.root / "scratch/wrapper.py").write_text("print('changed')\n")
        review_after = engineering.snapshot(self.root, ["scratch/"])
        self.assertEqual(engineering.compare(review, review_after, [])["violations"], ["scratch/wrapper.py"])

    def test_explicit_directory_audit_rejects_symlink_special_and_git_entries(self):
        (self.root / ".gitignore").write_text("scratch/\n")
        scratch = self.root / "scratch"
        scratch.mkdir()
        (scratch / "link").symlink_to(self.root / "source.py")
        with self.assertRaisesRegex(ValueError, "symlink or special"):
            engineering.snapshot(self.root, ["scratch/"])
        (scratch / "link").unlink()
        os.mkfifo(scratch / "pipe")
        with self.assertRaisesRegex(ValueError, "symlink or special"):
            engineering.snapshot(self.root, ["scratch/"])
        (scratch / "pipe").unlink()
        (scratch / ".git").mkdir()
        with self.assertRaisesRegex(ValueError, "Git metadata"):
            engineering.snapshot(self.root, ["scratch/"])

    def test_explicit_directory_audit_honors_file_and_byte_limits(self):
        (self.root / ".gitignore").write_text("scratch/\n")
        scratch = self.root / "scratch"
        scratch.mkdir()
        (scratch / "large.bin").write_bytes(b"x" * 513)
        with patch.object(engineering, "MAX_FILE_BYTES", 512):
            with self.assertRaisesRegex(ValueError, "file exceeds"):
                engineering.snapshot(self.root, ["scratch/"])
        with patch.object(engineering, "MAX_FILES", 3):
            with self.assertRaisesRegex(ValueError, "audited files"):
                engineering.snapshot(self.root, ["scratch/"])

    def test_private_copy_includes_explicit_ignored_directory(self):
        (self.root / ".gitignore").write_text("scratch/\n")
        (self.root / "scratch").mkdir()
        (self.root / "scratch/wrapper.py").write_text("print('fixture')\n")
        destination = self.root.parent / "copy"
        origin = engineering.copy_repository(self.root, destination, ["scratch/"])
        self.assertIn("scratch/wrapper.py", origin["files"])
        self.assertEqual((destination / "scratch/wrapper.py").read_text(), "print('fixture')\n")
        self.assertIn("scratch/wrapper.py", engineering.snapshot(destination)["files"])


if __name__ == "__main__":
    unittest.main()
