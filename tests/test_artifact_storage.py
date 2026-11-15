"""Offline raw-content admission checks in disposable Git repositories."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import engineering
import execution
from controller_store import Store


class ArtifactStorageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "repo"
        self.root.mkdir()
        self.git("init", "-q")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True).stdout

    def admit(self, name):
        engineering.validate_artifact_paths([self.root / name])

    def test_ignored_nonexistent_descendants_and_external_scratch(self):
        (self.root / ".gitignore").write_text("/.research-artifacts/\n")
        self.admit(".research-artifacts/not/yet/created/paper.pdf")
        self.assertFalse((self.root / ".research-artifacts").exists())
        engineering.validate_artifact_paths([self.root.parent / "external/paper.pdf"])

    def test_provider_directory_needs_whole_subtree_exclusion(self):
        destination = self.root / "operation/runtime-state"
        rule = self.root / ".gitignore"
        rule.write_text("/operation/runtime-state/database.sqlite\n")
        with self.assertRaisesRegex(ValueError, "effective repository .gitignore"):
            engineering.validate_artifact_paths([destination], directories=True)
        rule.write_text("/operation/runtime-state/\n")
        engineering.validate_artifact_paths([destination], directories=True)
        self.assertFalse(destination.exists())
        engineering.validate_artifact_paths([self.root.parent / "external/runtime-state"], directories=True)

    def test_reincluded_provider_directory_and_tracked_descendants_rejected(self):
        destination = self.root / "operation/runtime-state"
        rule = self.root / ".gitignore"
        rule.write_text("/operation/*\n!/operation/runtime-state/\n/operation/runtime-state/*.sqlite\n")
        with self.assertRaisesRegex(ValueError, "effective repository .gitignore"):
            engineering.validate_artifact_paths([destination], directories=True)
        rule.write_text("/operation/runtime-state/\n")
        destination.mkdir(parents=True)
        (destination / "old.sqlite").write_text("fixture")
        self.git("add", "-f", "operation/runtime-state/old.sqlite")
        with self.assertRaisesRegex(ValueError, "already tracked"):
            engineering.validate_artifact_paths([destination], directories=True)

    def test_provider_directory_contract_rejects_symlinks_curated_roots_and_repo_root(self):
        (self.root / ".gitignore").write_text("*\n")
        (self.root / "alias").symlink_to(self.root.parent, target_is_directory=True)
        for destination in (self.root / "alias", self.root / "research", self.root / "_ref", self.root):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                engineering.validate_artifact_paths([destination], directories=True)

    def test_unignored_and_negated_exact_file_rejected(self):
        with self.assertRaisesRegex(ValueError, "effective repository .gitignore"):
            self.admit("cache/paper.pdf")
        (self.root / ".gitignore").write_text("/cache/*\n!/cache/keep.pdf\n")
        self.admit("cache/paper.pdf")
        with self.assertRaisesRegex(ValueError, "effective repository .gitignore"):
            self.admit("cache/keep.pdf")

    def test_nested_negation_and_literal_paths(self):
        (self.root / ".gitignore").write_text("*.pdf\n")
        (self.root / "cache").mkdir()
        (self.root / "cache/.gitignore").write_text("!keep.pdf\n")
        self.admit("cache/[paper]\n.pdf")
        with self.assertRaisesRegex(ValueError, "effective repository .gitignore"):
            self.admit("cache/keep.pdf")

    def test_tracked_even_if_ignored_and_deleted_is_rejected(self):
        (self.root / "paper.pdf").write_bytes(b"fixture")
        self.git("add", "paper.pdf")
        (self.root / "paper.pdf").unlink()
        (self.root / ".gitignore").write_text("*.pdf\n")
        with self.assertRaisesRegex(ValueError, "already tracked"):
            self.admit("paper.pdf")

    def test_global_and_git_info_excludes_are_insufficient(self):
        (self.root / ".git/info/exclude").write_text("*.pdf\n")
        with self.assertRaisesRegex(ValueError, "this repository's .gitignore"):
            self.admit("paper.pdf")
        (self.root / ".git/info/exclude").write_text("")
        external = self.root.parent / ".gitignore"
        external.write_text("*.pdf\n")
        self.git("config", "core.excludesFile", str(external))
        with self.assertRaisesRegex(ValueError, "this repository's .gitignore"):
            self.admit("paper.pdf")
        self.git("config", "core.excludesFile", "../.gitignore")
        with self.assertRaisesRegex(ValueError, "this repository's .gitignore"):
            self.admit("paper.pdf")

    def test_authored_and_curated_directories_remain_protected_when_ignored(self):
        (self.root / ".gitignore").write_text("*\n")
        for name in ("research/paper.pdf", "studies/example/research/paper.pdf",
                     "_ref/paper.pdf", "_appraisal/paper.pdf"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "outside research"):
                self.admit(name)

    def test_symlinks_traversal_metadata_and_nonfiles_rejected(self):
        (self.root / ".gitignore").write_text("*\n")
        (self.root / "link").symlink_to(self.root.parent)
        (self.root / "file").write_text("fixture")
        (self.root / "directory").mkdir()
        for path in (self.root / "link/paper.pdf", self.root / "../paper.pdf",
                     self.root / ".git/paper.pdf", self.root / "file/paper.pdf",
                     self.root / "directory", Path("relative/paper.pdf")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                engineering.validate_artifact_paths([path])

    def test_linked_worktree_and_nested_repository_cannot_bypass_outer_rules(self):
        (self.root / ".gitignore").write_text("/cache/\n")
        self.git("add", ".gitignore")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "fixture")
        worktree = self.root.parent / "linked"
        self.git("worktree", "add", "--detach", str(worktree))
        engineering.validate_artifact_paths([worktree / "cache/paper.pdf"])
        nested = self.root / "nested"
        nested.mkdir()
        subprocess.run(["git", "-C", str(nested), "init", "-q"], check=True)
        (nested / ".gitignore").write_text("/cache/\n")
        # The nested .gitignore is also an in-tree ignore source for the outer
        # repository. An outer tracked file must nevertheless reject capture.
        engineering.validate_artifact_paths([nested / "cache/paper.pdf"])
        (nested / "cache").mkdir()
        (nested / "cache/paper.pdf").write_bytes(b"fixture")
        object_id = self.git("hash-object", "-w", "nested/cache/paper.pdf").decode().strip()
        self.git("update-index", "--add", "--cacheinfo", "100644", object_id, "nested/cache/paper.pdf")
        with self.assertRaisesRegex(ValueError, "already tracked"):
            engineering.validate_artifact_paths([nested / "cache/paper.pdf"])

    def test_git_inspection_failure_is_not_treated_as_external_scratch(self):
        with patch.object(engineering, "_git", side_effect=ValueError("inspection failed")):
            with self.assertRaisesRegex(ValueError, "inspection failed"):
                self.admit("cache/paper.pdf")

    def test_launch_refuses_raw_content_and_retains_nonlaunch_fence(self):
        directory = self.root / "unignored/operation"
        spec = {"argv": [sys.executable, "-c", "print('fixture')"], "cwd": str(self.root),
                "env": {}, "timeout_seconds": 2, "operation_id": "fixture"}
        with self.assertRaisesRegex(execution.NotLaunched, "effective repository .gitignore"):
            execution.launch(directory, spec)
        self.assertEqual({path.name for path in directory.iterdir()}, {"metadata.lock", "receipt.json"})
        observation = execution.observe(directory)
        self.assertTrue(observation["not_launched"])
        self.assertTrue(observation["released"])
        self.assertEqual(observation["state"], "setup_error")

    def test_empty_git_placeholder_is_not_a_repo_but_broken_metadata_fails(self):
        outside = self.root.parent / "external"
        outside.mkdir()
        marker = outside / ".git"
        marker.mkdir()
        engineering.validate_artifact_paths([outside / "cache/paper.pdf"])
        (marker / "broken").write_text("fixture")
        with self.assertRaisesRegex(ValueError, "repository inspection failed"):
            engineering.validate_artifact_paths([outside / "cache/paper.pdf"])

    def test_atomic_spec_validates_actual_temporary_path_before_creation(self):
        directory = self.root / "cache"
        directory.mkdir()
        (self.root / ".gitignore").write_text("/cache/spec.json\n")
        with self.assertRaisesRegex(ValueError, "effective repository .gitignore"):
            execution._write(directory / "spec.json", {"argv": ["source content"]}, artifact=True)
        self.assertEqual(list(directory.iterdir()), [])

    def test_capsule_refusal_preserves_original_and_creates_no_temporary(self):
        directory = self.root / "cache"
        directory.mkdir()
        destination = directory / "evidence.json"
        destination.write_text("original retained evidence")
        (self.root / ".gitignore").write_text("/cache/evidence.json\n")
        with self.assertRaisesRegex(ValueError, "effective repository .gitignore"):
            engineering.durable_json(destination, {"source": "new unadmitted content"})
        self.assertEqual(destination.read_text(), "original retained evidence")
        self.assertEqual(list(directory.iterdir()), [destination])

    def test_capsule_rename_failure_retains_admitted_capture_and_original(self):
        directory = self.root / "cache"
        directory.mkdir()
        destination = directory / "evidence.json"
        destination.write_text("original retained evidence")
        (self.root / ".gitignore").write_text("/cache/\n")
        with patch.object(engineering.os, "replace", side_effect=OSError("synthetic rename error")):
            with self.assertRaisesRegex(OSError, "synthetic rename error"):
                engineering.durable_json(destination, {"source": "retained new capture"})
        self.assertEqual(destination.read_text(), "original retained evidence")
        retained = list(directory.glob(".evidence-*"))
        self.assertEqual(len(retained), 1)
        self.assertIn("retained new capture", retained[0].read_text())

    def test_new_database_checks_sqlite_sidecars_but_recovery_remains_accessible(self):
        directory = self.root / "cache"
        (self.root / ".gitignore").write_text("/cache/state.sqlite3\n")
        with self.assertRaisesRegex(ValueError, "effective repository .gitignore"):
            Store(directory, create=True)
        self.assertFalse(directory.exists())
        (self.root / ".gitignore").write_text("/cache/\n")
        store = Store(directory, create=True)
        store.close()
        (self.root / ".gitignore").write_text("")
        store = Store(directory)
        store.close()

    def test_ignore_change_does_not_strand_owned_cancellation_or_delete_capture(self):
        directory = self.root / "cache/operation"
        rule = self.root / ".gitignore"
        rule.write_text("/cache/\n")
        spec = {"argv": [sys.executable, "-c", "import time; print('retained finding', flush=True); time.sleep(20)"],
                "cwd": str(self.root), "env": {}, "timeout_seconds": 20, "operation_id": "fixture"}
        try:
            execution.launch(directory, spec)
            end = time.monotonic() + 3
            while time.monotonic() < end:
                if (directory / "stdout").exists() and b"retained finding" in (directory / "stdout").read_bytes():
                    break
                time.sleep(.02)
            self.assertIn(b"retained finding", (directory / "stdout").read_bytes())
            rule.write_text("")
            execution.cancel(directory, "retain evidence and stop")
            end = time.monotonic() + 4
            while time.monotonic() < end:
                result = execution.observe(directory)
                if result.get("released"):
                    break
                time.sleep(.02)
            self.assertTrue(result.get("released"), result)
            self.assertEqual(result["state"], "cancelled")
            self.assertIn(b"retained finding", (directory / "stdout").read_bytes())
        finally:
            execution.cancel(directory, "test cleanup")
            end = time.monotonic() + 4
            while time.monotonic() < end and not execution.observe(directory).get("released"):
                time.sleep(.02)


if __name__ == "__main__":
    unittest.main()
