import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / "examples/verification_replay.py"


def load_module(path=SCRIPT):
    spec = importlib.util.spec_from_file_location("verification_replay_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def answer(scenario, phase):
    return {
        "scenario": scenario,
        "phase": phase,
        "source_units_consulted": [],
        "assignments": [{
            "id": f"{phase}-1", "action": "new", "dispatch": "now", "question": "Inspect a bounded question",
            "purpose": "Choose the next discriminator", "source_units": [], "model": "luna", "role": "scout",
            "conversation_id": "C1", "deliverable": "A short evidence note", "ownership": "Read only",
            "dependencies": [], "stop_condition": "One bounded discriminator", "model_reason": "Fits the task",
            "expected_work_operations": ["read source"]
        }]
    }


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.run = self.base / "replay"
        self.m = load_module()

    def prepare(self):
        self.m.checked_run_root(str(self.run), create=True)
        self.m.stage(self.run)

    def submit_all(self, phase):
        state = self.m.load_state(self.run)
        for pid, scenario in self.m.PARTICIPANTS.items():
            path = self.base / f"{pid}-{phase}.json"
            path.write_text(json.dumps(answer(scenario, phase)), encoding="utf-8")
            self.m.submit(self.run, pid, str(path))

    def test_phase_gate_locks_responses_and_releases_identical_scenario_bytes(self):
        self.prepare()
        with self.assertRaisesRegex(self.m.ReplayError, "missing initial submission"):
            self.m.advance(self.run)
        for pid, scenario in self.m.PARTICIPANTS.items():
            path = self.base / f"{pid}-initial.json"
            path.write_text(json.dumps(answer(scenario, "initial")), encoding="utf-8")
            self.m.submit(self.run, pid, str(path))
        self.m.advance(self.run)
        self.assertEqual(self.m.load_state(self.run)["phase"], "E1")
        c = (self.run / "releases/carrier/E1.json").read_bytes()
        r = (self.run / "releases/regression/E1.json").read_bytes()
        self.assertEqual(c, (self.run / "releases/carrier/E1.json").read_bytes())
        self.assertNotEqual(c, r)

    def test_phase_context_contains_only_own_history_and_ordered_events(self):
        self.prepare()
        self.submit_all("initial")
        self.m.advance(self.run)
        p17 = self.m.safe_json(self.run / "participants/p17/E1-request.json")
        p43 = self.m.safe_json(self.run / "participants/p43/E1-request.json")
        self.assertEqual([x["phase"] for x in p17["prior_responses"]], ["initial"])
        self.assertEqual([x["id"] for x in p17["released_events"]], ["E1"])
        self.assertEqual(p17["released_events"], p43["released_events"])
        self.assertNotIn("p43", json.dumps(p17))
        self.assertNotIn("E2", json.dumps(p17))
        self.submit_all("E1")
        self.m.advance(self.run)
        p17e2 = self.m.safe_json(self.run / "participants/p17/E2-request.json")
        self.assertEqual([x["phase"] for x in p17e2["prior_responses"]], ["initial", "E1"])
        self.assertEqual([x["id"] for x in p17e2["released_events"]], ["E1", "E2"])
        self.assertNotIn("p43", json.dumps(p17e2))

    def test_duplicate_malformed_and_wrong_phase_answers_rejected(self):
        self.prepare()
        path = self.base / "bad.json"
        path.write_text('{"phase":"initial","scenario":"carrier","assignments":[NaN]}', encoding="utf-8")
        with self.assertRaises(self.m.ReplayError):
            self.m.submit(self.run, "p17", str(path))
        path.write_text(json.dumps(answer("carrier", "E1")), encoding="utf-8")
        with self.assertRaisesRegex(self.m.ReplayError, "phase"):
            self.m.submit(self.run, "p17", str(path))
        valid = answer("carrier", "initial")
        valid["assignments"].append(valid["assignments"][0])
        path.write_text(json.dumps(valid), encoding="utf-8")
        with self.assertRaisesRegex(self.m.ReplayError, "stable id"):
            self.m.submit(self.run, "p17", str(path))

    def test_conflicting_duplicate_json_key_rejected_before_submission(self):
        self.prepare()
        path = self.base / "ambiguous.json"
        raw = json.dumps(answer("carrier", "initial"))
        path.write_text('{"scenario":"regression",' + raw[1:], encoding="utf-8")
        with self.assertRaisesRegex(self.m.ReplayError, "duplicate JSON key"):
            self.m.submit(self.run, "p17", str(path))
        self.assertFalse((self.run / "submissions/initial/p17.json").exists())

    def test_changed_staged_or_submitted_bytes_fail_before_advance(self):
        self.prepare()
        self.submit_all("initial")
        submission = self.run / "submissions/initial/p17.json"
        original = submission.read_bytes()
        submission.write_bytes(original + b" ")
        with self.assertRaisesRegex(self.m.ReplayError, "changed since lock"):
            self.m.advance(self.run)
        submission.write_bytes(original)
        (self.run / "participants/p17/scenario.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(self.m.ReplayError, "changed since lock"):
            self.m.advance(self.run)

    def test_scenario_developments_are_precommitted_before_release(self):
        relocated_study = self.base / "study"
        shutil.copytree(SOURCE / "verification/decision-routing-study-2026-10-28/common",
                        relocated_study / "common")
        self.m.STUDY = relocated_study
        self.prepare()
        developments = relocated_study / "common/carrier/developments.json"
        developments.write_bytes(developments.read_bytes() + b" ")
        with self.assertRaisesRegex(self.m.ReplayError, "changed since prepare"):
            self.m.advance(self.run)
        self.assertFalse((self.run / "releases/carrier/E1.json").exists())

    def test_untracked_files_and_symlinks_in_run_are_rejected(self):
        self.prepare()
        surprise = self.run / "participants/p17/gold-answer.json"
        surprise.write_text('{"gold":true}', encoding="utf-8")
        with self.assertRaisesRegex(self.m.ReplayError, "unexpected=.*gold-answer"):
            self.m.advance(self.run)
        surprise.unlink()
        (self.run / "untracked-link").symlink_to(self.base / "outside.json")
        with self.assertRaisesRegex(self.m.ReplayError, "symlink is not allowed"):
            self.m.advance(self.run)

    def test_both_arms_receive_the_same_complete_scenario_source_inventory(self):
        self.prepare()
        p61 = {p.name: p.read_bytes() for p in (self.run / "participants/p61/sources").iterdir()}
        p29 = {p.name: p.read_bytes() for p in (self.run / "participants/p29/sources").iterdir()}
        expected = {f"R{n:02}.txt" for n in range(1, 14)}
        self.assertEqual(set(p61), expected)
        self.assertEqual(set(p29), expected)
        # This equality assertion fails against the earlier 10-versus-13 staging behavior.
        self.assertEqual(p61, p29)

    def test_missing_input_traversal_and_symlink_escape_rejected(self):
        with self.assertRaisesRegex(self.m.ReplayError, "missing input"):
            self.m.safe_rel(self.base, "absent.md")
        with self.assertRaisesRegex(self.m.ReplayError, "unsafe relative"):
            self.m.safe_rel(self.base, "../escape")
        outside = self.base / "outside.txt"
        outside.write_text("secret", encoding="utf-8")
        (self.base / "link.txt").symlink_to(outside)
        with self.assertRaisesRegex(self.m.ReplayError, "symlink input"):
            self.m.safe_rel(self.base, "link.txt")

    def test_run_root_inside_source_tree_rejected(self):
        with self.assertRaisesRegex(self.m.ReplayError, "outside the repository"):
            self.m.checked_run_root(str(SOURCE / "verification/unsafe"), create=True)

    def test_export_contains_only_allowed_inputs_for_20_cases(self):
        self.m.checked_run_root(str(self.run), create=True)
        self.m.export_research(self.run)
        root = self.run / "research-inputs"
        case_dirs = [p for p in root.glob("*/*") if p.is_dir()]
        self.assertEqual(len(case_dirs), 20)
        self.assertTrue((root / "pilot/r139/task.md").is_file())
        self.assertTrue((root / "continuation/n154/discovery.json").is_file())
        for path in root.rglob("*"):
            if path.is_file():
                self.assertNotIn(path.name, {"report.json", "arm-map.json", "analysis.json"})
        self.assertFalse(any("report.json" in p.parts for p in root.rglob("*")))

    def test_export_ignores_nontext_source_extras(self):
        research = self.base / "research"
        for group, count in (("pilot", 12), ("continuation/cases", 8)):
            for i in range(count):
                case = research / group / f"case{i:02}"
                (case / "sources").mkdir(parents=True)
                for name in ("contract.md", "task.md", "schema.json"):
                    (case / name).write_text("fixture", encoding="utf-8")
                (case / "sources/valid.txt").write_text("source excerpt", encoding="utf-8")
                (case / "sources/report.json").write_text('{"answer":"private"}', encoding="utf-8")
                (case / "sources/secret.other").write_text("exclude", encoding="utf-8")
        self.m.RESEARCH = research
        self.m.checked_run_root(str(self.run), create=True)
        self.m.export_research(self.run)
        exported = self.run / "research-inputs/pilot/case00/sources"
        self.assertEqual([p.name for p in exported.iterdir()], ["valid.txt"])

    def test_relocated_copy_uses_script_location_not_cwd(self):
        relocated = self.base / "relocated-kit"
        (relocated / "examples").mkdir(parents=True)
        shutil.copy2(SCRIPT, relocated / "examples/verification_replay.py")
        (relocated / "verification").mkdir()
        shutil.copytree(SOURCE / "verification/decision-routing-study-2026-10-28",
                        relocated / "verification/decision-routing-study-2026-10-28",
                        ignore=shutil.ignore_patterns("analysis", "locked", "views", "working"))
        shutil.copytree(SOURCE / "verification/luna-research-prompt-study-2026-10-28/pilot",
                        relocated / "verification/luna-research-prompt-study-2026-10-28/pilot")
        shutil.copytree(SOURCE / "verification/luna-research-prompt-study-2026-10-28/continuation/cases",
                        relocated / "verification/luna-research-prompt-study-2026-10-28/continuation/cases")
        m = load_module(relocated / "examples/verification_replay.py")
        m.checked_run_root(str(self.run), create=True)
        old = Path.cwd()
        try:
            import os
            os.chdir(self.base)
            m.stage(self.run)
        finally:
            os.chdir(old)
        self.assertTrue((self.run / "participants/p17/sources/H01.txt").is_file())
        self.assertFalse((self.run / "participants/p17/initial.json").exists())

    def test_completion_after_e2_and_no_extra_advance(self):
        self.prepare()
        for phase in ("initial", "E1", "E2"):
            self.submit_all(phase)
            self.m.advance(self.run)
        self.assertEqual(self.m.load_state(self.run)["status"], "complete")
        with self.assertRaisesRegex(self.m.ReplayError, "cannot advance"):
            self.m.advance(self.run)


if __name__ == "__main__":
    unittest.main()
