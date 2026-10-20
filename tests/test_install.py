"""Disposable filesystem tests; never read or write the real Codex home."""

import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).absolute().parents[1] / "install.py"
SPEC = importlib.util.spec_from_file_location("delegation_install", MODULE_PATH)
kit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = kit
SPEC.loader.exec_module(kit)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.home = self.root / "codex"
        self.home.mkdir()
        for name in kit.FILES:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'model = "fixture"\n' if name.endswith(".toml") else b"# fixture\n")
            path.chmod(0o640)
        self.agents = self.home / "AGENTS.md"
        self.config = self.home / "config.toml"
        self.agents.write_bytes(b"Keep local instructions exactly.\n")
        self.agents.chmod(0o640)
        self.config.write_bytes(b'model = "primary"\nmodel_reasoning_effort = "ultra"')
        self.config.chmod(0o600)
        self.original = {path: kit.read_state(path) for path in (self.agents, self.config)}

    def activate(self):
        kit.apply(kit.plan(self.home, self.source))

    def assert_original(self):
        for path, state in self.original.items():
            self.assertEqual(kit.read_state(path), state)

    def test_roundtrip_exact_bytes_and_modes(self):
        self.activate()
        loaded = kit.parse_toml(self.config.read_bytes(), self.config)
        self.assertEqual(loaded["model"], "primary")
        self.assertEqual(loaded["model_reasoning_effort"], "ultra")
        self.assertEqual(set(loaded["agents"]), set(kit.ROLES))
        self.assertNotIn("subagent_model", loaded)
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertTrue((self.home / "delegation-kit" / "policy.md").exists())
        self.assertTrue(list((self.home / "delegation-kit" / ".installation" / "backups").rglob("config.toml")))

    def test_preserves_intervening_unrelated_edits(self):
        self.activate()
        self.agents.write_bytes(b"Added before.\n" + self.agents.read_bytes() + b"Added after.\n")
        self.config.write_bytes(b"# user note\n" + self.config.read_bytes() + b"\n[history]\npersistence = \"save-all\"\n")
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(self.agents.read_bytes(), b"Added before.\n" + self.original[self.agents].data + b"Added after.\n")
        self.assertEqual(self.config.read_bytes(), b"# user note\n" + self.original[self.config].data + b"\n[history]\npersistence = \"save-all\"\n")

    def test_idempotent_install_disable_and_reactivation(self):
        self.activate()
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_absent_globals_removed_only_if_still_empty(self):
        self.agents.unlink()
        self.config.unlink()
        self.activate()
        self.config.write_bytes(self.config.read_bytes() + b"# new user content\n")
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertFalse(self.agents.exists())
        self.assertEqual(self.config.read_bytes(), b"# new user content\n")

    def test_preflight_refuses_override_conflicts_and_corrupt_toml(self):
        cases = (
            ("AGENTS.override.md", b"This suppresses AGENTS.md\n"),
            ("config.toml", b"[agents.luna_worker]\nmodel = 'mine'\n"),
            ("config.toml", b"not = valid = toml\n"),
            ("config.toml", b"agents = 4\n"),
        )
        for name, data in cases:
            with self.subTest(name=name, data=data):
                path = self.home / name
                before = kit.read_state(path)
                path.write_bytes(data)
                with self.assertRaises(kit.Refusal):
                    kit.plan(self.home, self.source)
                self.assertFalse((self.home / "delegation-kit").exists())
                if before.data is None:
                    path.unlink()
                else:
                    path.write_bytes(before.data)

    def test_modified_or_incomplete_block_refused(self):
        self.activate()
        initial = self.agents.read_bytes()
        self.agents.write_bytes(initial.replace(b"Preserve the user's", b"Ignore the user's"))
        for uninstall in (False, True):
            with self.assertRaises(kit.Refusal):
                kit.plan(self.home, self.source, uninstall)
        self.agents.write_bytes(initial.replace(kit.END.encode(), b""))
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source, True)

    def test_standalone_internal_names_and_ambiguous_files_refused(self):
        directory = self.home / "agents"
        directory.mkdir()
        path = directory / "different_filename.toml"
        for contents in (
            b'name = "luna_worker"\n',
            b'model = "unknown-name"\n',
            b'name = 17\n',
            b'name = invalid = toml\n',
        ):
            with self.subTest(contents=contents):
                path.write_bytes(contents)
                with self.assertRaises(kit.Refusal):
                    kit.plan(self.home, self.source)
                self.assertFalse((self.home / "delegation-kit").exists())
        path.write_bytes(b'name = "unrelated_reviewer"\n')
        self.activate()
        self.assertEqual(path.read_bytes(), b'name = "unrelated_reviewer"\n')

    def test_symlink_sources_and_destinations_refused(self):
        original = self.source / "policy.md"
        original.rename(self.source / "policy-real.md")
        original.symlink_to(self.source / "policy-real.md")
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source)
        original.unlink()
        (self.source / "policy-real.md").rename(original)
        self.config.rename(self.home / "config-real.toml")
        self.config.symlink_to(self.home / "config-real.toml")
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source)

    def test_modified_bundle_not_overwritten(self):
        self.activate()
        installed = self.home / "delegation-kit" / "policy.md"
        installed.write_bytes(b"my local changes\n")
        with self.assertRaises(kit.Refusal):
            kit.plan(self.home, self.source)
        self.assertEqual(installed.read_bytes(), b"my local changes\n")

    def test_concurrent_global_edit_is_preserved(self):
        changes = kit.plan(self.home, self.source)
        self.config.write_bytes(b'model = "new choice"\n')
        with self.assertRaises(kit.Refusal):
            kit.apply(changes)
        self.assertEqual(self.config.read_bytes(), b'model = "new choice"\n')
        self.assertFalse((self.home / "delegation-kit").exists())

    def test_every_staging_failure_leaves_globals_and_no_partial_bundle(self):
        changes = kit.plan(self.home, self.source)
        original_stage = kit._stage
        for failing_index in range(1, len(changes) + 1):
            with self.subTest(failing_index=failing_index):
                count = 0

                def fail_once(*arguments):
                    nonlocal count
                    count += 1
                    if count == failing_index:
                        raise OSError("simulated staging write failure")
                    return original_stage(*arguments)

                with mock.patch.object(kit, "_stage", side_effect=fail_once):
                    with self.assertRaises(OSError):
                        kit.apply(changes)
                self.assert_original()
                self.assertFalse((self.home / "delegation-kit").exists())

    def test_every_atomic_replace_failure_rolls_back(self):
        changes = kit.plan(self.home, self.source)
        original_replace = os.replace
        for failing_index in range(1, len(changes) + 1):
            with self.subTest(failing_index=failing_index):
                count = 0

                def fail_once(*arguments):
                    nonlocal count
                    count += 1
                    if count == failing_index:
                        raise OSError("simulated replacement failure")
                    return original_replace(*arguments)

                with mock.patch.object(kit.os, "replace", side_effect=fail_once):
                    with self.assertRaises(OSError):
                        kit.apply(changes)
                self.assert_original()
                self.assertFalse((self.home / "delegation-kit").exists())

    def test_uninstall_failure_rolls_back_active_configuration(self):
        self.activate()
        active = {path: kit.read_state(path) for path in (self.agents, self.config)}
        changes = kit.plan(self.home, self.source, uninstall=True)
        original_replace = os.replace
        count = 0

        def fail_once(*arguments):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("simulated disable failure")
            return original_replace(*arguments)

        with mock.patch.object(kit.os, "replace", side_effect=fail_once):
            with self.assertRaises(OSError):
                kit.apply(changes)
        for path, state in active.items():
            self.assertEqual(kit.read_state(path), state)
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_uninstall_failure_restores_newly_created_globals_after_deletion(self):
        self.agents.unlink()
        self.config.unlink()
        self.activate()
        active = {path: kit.read_state(path) for path in (self.agents, self.config)}
        changes = kit.plan(self.home, self.source, uninstall=True)
        original_replace = os.replace
        count = 0

        def fail_once(*arguments):
            nonlocal count
            count += 1
            if count == 1:
                raise OSError("failure after removing globals")
            return original_replace(*arguments)

        with mock.patch.object(kit.os, "replace", side_effect=fail_once):
            with self.assertRaises(OSError):
                kit.apply(changes)
        for path, state in active.items():
            self.assertEqual(kit.read_state(path), state)
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_preview_is_read_only(self):
        with mock.patch("sys.stdout"):
            self.assertEqual(kit.main(["--home", str(self.home), "--source", str(self.source)]), 0)
        self.assert_original()
        self.assertFalse((self.home / "delegation-kit").exists())


if __name__ == "__main__":
    unittest.main()
