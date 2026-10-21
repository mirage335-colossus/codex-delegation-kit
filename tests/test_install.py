"""Disposable filesystem tests; never read or write the real Codex home."""

import importlib.util
import json
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

    def seed_legacy(self, *, active=True):
        """Create the prior eight-file version-1 installation layout."""
        return self.seed_layout(kit.LEGACY_FILES, kit.LEGACY_ROLES, active=active)

    def seed_advisory(self, *, active=True):
        """Create the eleven-file, six-role layout before controller support."""
        return self.seed_layout(kit.ADVISORY_FILES, kit.ROLES, active=active)

    def seed_controller(self, *, active=True):
        """Create the seventeen-file controller layout before engineering support."""
        return self.seed_layout(kit.CONTROLLER_FILES, kit.ROLES, active=active)

    def seed_layout(self, files, roles, *, active):
        target = self.home / "delegation-kit"
        for name in files:
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((self.source / name).read_bytes())
        activation = {}
        for name, block in kit.blocks(target, roles).items():
            path = self.home / name
            before = kit.read_state(path)
            text = (before.data or b"").decode()
            inserted = ("\n" if text and not text.endswith("\n") else "") + block
            activation[name] = {"inserted": inserted, "original_exists": before.data is not None}
            if active:
                path.write_bytes((text + inserted).encode())
        manifest_path = target / ".installation/manifest.json"
        manifest_path.parent.mkdir()
        manifest_path.write_text(json.dumps({
            "version": 1, "home": str(self.home), "active": active,
            "activation": activation,
            "bundle_digests": {name: kit.digest((target / name).read_bytes())
                               for name in files},
            "last_backups": [],
        }))
        return target

    def snapshot_home(self):
        return {path.relative_to(self.home): kit.read_state(path)
                for path in self.home.rglob("*") if path.is_file()}

    def test_active_legacy_upgrade_preserves_config_position_history_and_roundtrip(self):
        target = self.seed_legacy()
        self.config.write_bytes(self.config.read_bytes() + b'\n[history]\npersistence = "save-all"\n')
        before = self.config.read_bytes()
        old_block = kit.blocks(target, kit.LEGACY_ROLES)["config.toml"].encode()
        historical = target / ".installation/backups/older-transaction/config.toml"
        historical.parent.mkdir(parents=True)
        historical.write_bytes(b"earlier user configuration\n")
        evidence = target / "state/prior-assignment/result.json"
        evidence.parent.mkdir(parents=True)
        evidence.write_bytes(b'{"status": "completed"}\n')
        history = {path: path.read_bytes() for path in (historical, evidence)}

        self.activate()
        self.assertEqual(self.config.read_bytes(), before.replace(old_block, kit.blocks(target)["config.toml"].encode()))
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(manifest["version"], 1)
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(manifest["source_directory"], str(self.source.absolute()))
        loaded = kit.parse_toml(self.config.read_bytes(), self.config)
        self.assertEqual(set(loaded["agents"]), set(kit.ROLES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        self.assertEqual({path: path.read_bytes() for path in history}, history)

        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assertEqual(kit.read_state(self.agents), self.original[self.agents])
        self.assertEqual(self.config.read_bytes(), self.original[self.config].data + b'\n[history]\npersistence = "save-all"\n')
        self.assertEqual({path: path.read_bytes() for path in history}, history)

    def test_inactive_legacy_installation_upgrades_and_roundtrips(self):
        target = self.seed_legacy(active=False)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()

    def test_active_legacy_can_be_disabled_before_upgrade(self):
        self.seed_legacy()
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.activate()
        self.assertEqual(set(kit.parse_toml(self.config.read_bytes(), self.config)["agents"]), set(kit.ROLES))

    def test_legacy_upgrade_refuses_unowned_new_role_even_with_identical_bytes(self):
        target = self.seed_legacy()
        name = "agents/inherited_worker.toml"
        (target / name).write_bytes((self.source / name).read_bytes())
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "not owned"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

    def test_unknown_manifest_inventory_is_refused_without_writes(self):
        self.activate()
        path = self.home / "delegation-kit/.installation/manifest.json"
        manifest = json.loads(path.read_text())
        manifest["bundle_digests"]["unexpected-file"] = "unrecognized"
        path.write_text(json.dumps(manifest))
        before = self.snapshot_home()
        for uninstall in (False, True):
            with self.subTest(uninstall=uninstall), self.assertRaisesRegex(kit.Refusal, "unexpected bundle file list"):
                kit.plan(self.home, self.source, uninstall=uninstall)
            self.assertEqual(self.snapshot_home(), before)

    def test_advisory_upgrade_preserves_activation_and_retained_controller_state(self):
        target = self.seed_advisory()
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}
        retained = target / "state/owned-run/state.sqlite3"
        retained.parent.mkdir(parents=True)
        retained.write_bytes(b"retained database fixture; not an installer input\n")
        receipt = target / "state/owned-run/operations/op-1/receipt.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_bytes(b'{"operation_id":"op-1","state":"running"}\n')
        history = {path: path.read_bytes() for path in (retained, receipt)}

        preview = kit.plan(self.home, self.source)
        self.assertTrue(preview)
        self.assertEqual({path: kit.read_state(path) for path in globals_before}, globals_before)
        kit.apply(preview)
        self.assertEqual({path: kit.read_state(path) for path in globals_before}, globals_before)
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        for name in kit.FILES:
            self.assertEqual((target / name).read_bytes(), (self.source / name).read_bytes())
        self.assertEqual(kit.plan(self.home, self.source), [])
        self.assertEqual({path: path.read_bytes() for path in history}, history)
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertEqual({path: path.read_bytes() for path in history}, history)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_inactive_advisory_upgrade_and_disable_before_upgrade(self):
        target = self.seed_advisory(active=False)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()

    def test_active_advisory_can_be_disabled_without_installing_controller(self):
        target = self.seed_advisory()
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertFalse((target / "controller.py").exists())
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.ADVISORY_FILES))

    def test_advisory_upgrade_refuses_unowned_controller_even_with_identical_bytes(self):
        target = self.seed_advisory()
        name = "controller.py"
        (target / name).write_bytes((self.source / name).read_bytes())
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "not owned"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

    def test_controller_upgrade_preserves_activation_owned_execution_and_history(self):
        target = self.seed_controller()
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}
        retained = {
            target / "state/run/state.sqlite3": b"retained scheduling database\n",
            target / "state/run/operations/op-1/receipt.json": b'{"state":"running","released":false}\n',
            target / "state/run/operations/op-1/patch.diff": b"retained original patch\n",
            target / ".installation/backups/old/manifest.json": b"retained historical manifest\n",
        }
        for path, contents in retained.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)

        preview = kit.plan(self.home, self.source)
        self.assertTrue(any(change.path == target / "engineering.py" for change in preview))
        self.assertFalse((target / "engineering.py").exists())
        kit.apply(preview)
        self.assertEqual({path: kit.read_state(path) for path in globals_before}, globals_before)
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(len(manifest["bundle_digests"]), 18)
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual((target / "engineering.py").read_bytes(), (self.source / "engineering.py").read_bytes())
        self.assertEqual(kit.plan(self.home, self.source), [])
        self.assertEqual({path: path.read_bytes() for path in retained}, retained)

        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertTrue((target / "engineering.py").is_file())
        self.assertEqual({path: path.read_bytes() for path in retained}, retained)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])

    def test_inactive_controller_upgrade_and_idempotent_disable(self):
        target = self.seed_controller(active=False)
        self.assertEqual(kit.plan(self.home, self.source, uninstall=True), [])
        self.activate()
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertTrue(manifest["active"])
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.FILES))
        self.assertEqual(kit.plan(self.home, self.source), [])
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()

    def test_controller_can_be_disabled_without_installing_engineering(self):
        target = self.seed_controller()
        kit.apply(kit.plan(self.home, self.source, uninstall=True))
        self.assert_original()
        self.assertFalse((target / "engineering.py").exists())
        manifest = json.loads((target / ".installation/manifest.json").read_text())
        self.assertEqual(set(manifest["bundle_digests"]), set(kit.CONTROLLER_FILES))

    def test_controller_upgrade_refuses_unowned_engineering_even_with_identical_bytes(self):
        target = self.seed_controller()
        (target / "engineering.py").write_bytes((self.source / "engineering.py").read_bytes())
        before = self.snapshot_home()
        with self.assertRaisesRegex(kit.Refusal, "not owned"):
            kit.plan(self.home, self.source)
        self.assertEqual(self.snapshot_home(), before)

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

    def test_source_provenance_refreshes_for_identical_relocated_bundle(self):
        self.activate()
        target = self.home / "delegation-kit"
        manifest_path = target / ".installation/manifest.json"
        original_manifest = json.loads(manifest_path.read_text())
        self.assertEqual(original_manifest["source_directory"], str(self.source.absolute()))
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}
        relocated = self.root / "relocated source"
        self.source.rename(relocated)

        changes = kit.plan(self.home, relocated)
        self.assertTrue(changes)
        kit.apply(changes)
        updated = json.loads(manifest_path.read_text())
        self.assertEqual(updated["source_directory"], str(relocated.absolute()))
        self.assertEqual(updated["bundle_digests"], original_manifest["bundle_digests"])
        self.assertEqual({path: kit.read_state(path) for path in globals_before}, globals_before)
        self.assertEqual(kit.plan(self.home, relocated), [])

    def test_current_manifest_without_source_provenance_upgrades(self):
        self.activate()
        manifest_path = self.home / "delegation-kit/.installation/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest.pop("source_directory")
        manifest_path.write_text(json.dumps(manifest))
        globals_before = {path: kit.read_state(path) for path in (self.agents, self.config)}

        self.activate()
        updated = json.loads(manifest_path.read_text())
        self.assertEqual(updated["source_directory"], str(self.source.absolute()))
        self.assertEqual(updated["bundle_digests"], manifest["bundle_digests"])
        self.assertEqual({path: kit.read_state(path) for path in globals_before}, globals_before)
        self.assertEqual(kit.plan(self.home, self.source), [])

    def test_installed_copy_reinstall_and_disable_preserve_source_provenance(self):
        self.activate()
        target = self.home / "delegation-kit"
        manifest_path = target / ".installation/manifest.json"
        self.assertEqual(kit.plan(self.home, target), [])

        kit.apply(kit.plan(self.home, target, uninstall=True))
        disabled = json.loads(manifest_path.read_text())
        self.assertFalse(disabled["active"])
        self.assertEqual(disabled["source_directory"], str(self.source.absolute()))
        kit.apply(kit.plan(self.home, target))
        reactivated = json.loads(manifest_path.read_text())
        self.assertTrue(reactivated["active"])
        self.assertEqual(reactivated["source_directory"], str(self.source.absolute()))
        self.assertEqual(kit.plan(self.home, target), [])

    def test_installed_copy_cannot_invent_missing_source_provenance(self):
        self.activate()
        target = self.home / "delegation-kit"
        manifest_path = target / ".installation/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest.pop("source_directory")
        manifest_path.write_text(json.dumps(manifest))

        kit.apply(kit.plan(self.home, target))
        self.assertNotIn("source_directory", json.loads(manifest_path.read_text()))
        self.assertEqual(kit.plan(self.home, target), [])

    def test_source_provenance_normalizes_external_and_deployment_aliases(self):
        source_alias = self.source / ".." / self.source.name
        kit.apply(kit.plan(self.home, source_alias))
        target = self.home / "delegation-kit"
        manifest_path = target / ".installation/manifest.json"
        self.assertEqual(json.loads(manifest_path.read_text())["source_directory"], str(self.source.resolve()))
        target_alias = target / ".." / target.name
        self.assertEqual(kit.plan(self.home, target_alias), [])

    def test_malformed_source_provenance_is_refused_without_writes(self):
        self.activate()
        manifest_path = self.home / "delegation-kit/.installation/manifest.json"
        original = manifest_path.read_bytes()
        for value in (None, 42, [], "", "relative/source", "/source\0invalid"):
            with self.subTest(value=value):
                manifest = json.loads(original)
                manifest["source_directory"] = value
                manifest_path.write_text(json.dumps(manifest))
                before = self.snapshot_home()
                for uninstall in (False, True):
                    with self.assertRaises(kit.Refusal):
                        kit.plan(self.home, self.source, uninstall=uninstall)
                    self.assertEqual(self.snapshot_home(), before)
        manifest_path.write_bytes(original)

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
            ("config.toml", b"[agents.inherited_worker]\nconfig_file = 'personal.toml'\n"),
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
            b'name = "inherited_worker"\n',
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
