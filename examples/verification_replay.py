#!/usr/bin/env python3
"""Offline staging and sequential replay for the published verification packets.

This is a finite, manual-input workflow. It never calls a model or network.
Run roots are user-chosen directories outside the source checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any


REPO = Path(__file__).resolve().parents[1]
STUDY = REPO / "verification/decision-routing-study-2026-10-28"
RESEARCH = REPO / "verification/luna-research-prompt-study-2026-10-28"
PARTICIPANTS = {"p17": "carrier", "p43": "carrier", "p61": "regression", "p29": "regression"}
POLICY = {"p17": "policy-A.md", "p43": "policy-B.md", "p61": "policy-A.md", "p29": "policy-B.md"}
PHASES = ("initial", "E1", "E2")
REQUIRED = ("id", "action", "dispatch", "question", "purpose", "source_units", "model", "role",
            "conversation_id", "deliverable", "ownership", "dependencies", "stop_condition",
            "model_reason", "expected_work_operations")
MARKER = ".verification-replay.json"


class ReplayError(Exception):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def safe_json(path: Path) -> Any:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value = {}
        for key, item in pairs:
            if key in value:
                raise ReplayError(f"duplicate JSON key {key!r} in {path.name}")
            value[key] = item
        return value
    def bad_constant(value: str) -> None:
        raise ReplayError(f"invalid JSON constant {value} in {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=bad_constant,
                          object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReplayError(f"cannot read valid UTF-8 JSON at {path}: {exc}") from exc


def is_under(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def checked_run_root(raw: str, *, create: bool = False) -> Path:
    root = Path(raw).expanduser().absolute()
    # Do not allow outputs in the source tree or its verification evidence.
    if is_under(root.resolve(strict=False), REPO.resolve()) or is_under(root.resolve(strict=False), STUDY.resolve()):
        raise ReplayError("--run-dir must be outside the repository and verification source files")
    if create:
        root.mkdir(parents=True, exist_ok=True)
    if not root.exists() or not root.is_dir():
        raise ReplayError(f"run directory does not exist: {root}")
    if root.is_symlink():
        raise ReplayError("run directory may not be a symlink")
    resolved = root.resolve(strict=True)
    if is_under(resolved, REPO.resolve()):
        raise ReplayError("resolved --run-dir is inside the repository")
    for p in (root, *root.parents):
        if p.exists() and p.is_symlink():
            raise ReplayError(f"symlink path component is not allowed: {p}")
    return resolved


def safe_rel(base: Path, rel: str) -> Path:
    p = Path(rel)
    if p.is_absolute() or ".." in p.parts:
        raise ReplayError(f"unsafe relative path: {rel}")
    src = base / p
    if src.is_symlink():
        raise ReplayError(f"symlink input is not allowed: {rel}")
    try:
        resolved = src.resolve(strict=True)
    except OSError as exc:
        raise ReplayError(f"missing input file: {rel}") from exc
    if not is_under(resolved, base.resolve()):
        raise ReplayError(f"input escapes its source directory: {rel}")
    if not resolved.is_file():
        raise ReplayError(f"missing input file: {rel}")
    return resolved


def write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise ReplayError(f"refusing to overwrite existing file: {path}")
    path.write_bytes(data)


def load_state(root: Path) -> dict[str, Any]:
    marker = root / MARKER
    if not marker.is_file() or marker.is_symlink():
        raise ReplayError(f"not an initialized replay run: {root}")
    state = safe_json(marker)
    if state.get("format") != 1 or not isinstance(state.get("files"), dict):
        raise ReplayError("unsupported or malformed replay state")
    return state


def integrity(root: Path, state: dict[str, Any]) -> None:
    expected = set(state["files"])
    actual: set[str] = set()
    for current, dirs, files in os.walk(root, followlinks=False):
        here = Path(current)
        for name in list(dirs):
            child = here / name
            if child.is_symlink():
                raise ReplayError(f"symlink is not allowed in run directory: {child.relative_to(root)}")
        for name in files:
            path = here / name
            rel = path.relative_to(root).as_posix()
            if rel == MARKER:
                continue
            if path.is_symlink():
                raise ReplayError(f"symlink is not allowed in run directory: {rel}")
            actual.add(rel)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        raise ReplayError(f"run directory contents changed: missing={missing}, unexpected={unexpected}")
    for rel, expected in state["files"].items():
        path = safe_rel(root, rel)
        if digest(path.read_bytes()) != expected:
            raise ReplayError(f"staged or submitted file changed since lock: {rel}")


def development_hashes() -> dict[str, str]:
    base = STUDY / "common"
    result = {}
    for scenario in ("carrier", "regression"):
        path = safe_rel(base, f"{scenario}/developments.json")
        result[scenario] = digest(path.read_bytes())
    return result


def verify_developments(state: dict[str, Any]) -> None:
    current = development_hashes()
    if current != state.get("development_sha256"):
        raise ReplayError("scenario developments changed since prepare; refusing to release an event")


def record_file(root: Path, state: dict[str, Any], rel: str, data: bytes) -> None:
    path = root / rel
    write_new(path, data)
    state["files"][rel] = digest(data)


def participant_inputs(pid: str) -> list[tuple[str, Path]]:
    scenario = PARTICIPANTS[pid]
    base = STUDY / "common"
    srcs = safe_rel(base, f"{scenario}/scenario.md")
    files = [("contract.md", safe_rel(base, "contract.md")),
             ("routing.md", safe_rel(base, POLICY[pid])),
             ("scenario.md", srcs),
             ("decision-schema.json", safe_rel(base, "decision-schema.json"))]
    source_ids = list(range(1, 13)) if scenario == "carrier" else list(range(1, 14))
    prefix = "H" if scenario == "carrier" else "R"
    for n in source_ids:
        name = f"{prefix}{n:02}.txt"
        rel = f"{scenario}/sources/{name}"
        files.append((f"sources/{name}", safe_rel(base, rel)))
    return files


def request_doc(pid: str, phase: str = "initial", previous: list[dict[str, Any]] | None = None,
                releases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"study": "decision-routing planning replay", "participant": pid,
            "scenario": PARTICIPANTS[pid], "phase": phase,
            "instructions": "Read only the files in this participant directory. Submit one JSON decision object matching decision-schema.json. This is a planning exercise; do not run project tests, builds, web research, or models.",
            "prior_responses": previous or [], "released_events": releases or []}


def stage(run: Path) -> None:
    if any(run.iterdir()):
        raise ReplayError("new run directory must be empty")
    state: dict[str, Any] = {"format": 1, "phase": "initial", "status": "active", "files": {}, "locks": [],
                             "development_sha256": development_hashes()}
    for pid in PARTICIPANTS:
        out = run / "participants" / pid
        for rel, source in participant_inputs(pid):
            record_file(run, state, f"participants/{pid}/{rel}", source.read_bytes())
        request = request_doc(pid)
        record_file(run, state, f"participants/{pid}/request.json", json_bytes(request))
        msgs = [{"role": "system", "content": request["instructions"]},
                {"role": "user", "content": "Use only the attached participant materials; submit an initial plan."}]
        record_file(run, state, f"participants/{pid}/messages.json", json_bytes(msgs))
    (run / MARKER).write_bytes(json_bytes(state))


def validate_answer(value: Any, pid: str, phase: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReplayError("answer must be a JSON object")
    if value.get("scenario") != PARTICIPANTS[pid] or value.get("phase") != phase:
        raise ReplayError(f"answer must set scenario={PARTICIPANTS[pid]!r} and phase={phase!r}")
    if not isinstance(value.get("source_units_consulted"), list) or not isinstance(value.get("assignments"), list):
        raise ReplayError("source_units_consulted and assignments must be arrays")
    ids: set[str] = set()
    for n, row in enumerate(value["assignments"], 1):
        if not isinstance(row, dict):
            raise ReplayError(f"assignment {n} must be an object")
        missing = [key for key in REQUIRED if key not in row]
        if missing:
            raise ReplayError(f"assignment {n} missing fields: {', '.join(missing)}")
        ident = row["id"]
        if not isinstance(ident, str) or not ident.strip() or ident in ids:
            raise ReplayError(f"assignment {n} needs a unique nonempty stable id")
        ids.add(ident)
        for key in ("source_units", "dependencies", "expected_work_operations"):
            if not isinstance(row[key], list):
                raise ReplayError(f"assignment {n} field {key} must be an array")
        for key in ("action", "dispatch", "question", "purpose", "model", "role", "conversation_id",
                    "deliverable", "ownership", "stop_condition", "model_reason"):
            if not isinstance(row[key], str) or not row[key].strip():
                raise ReplayError(f"assignment {n} field {key} must be a nonempty string")
    return value


def submit(run: Path, pid: str, answer_file: str) -> None:
    if pid not in PARTICIPANTS:
        raise ReplayError(f"unknown participant: {pid}")
    state = load_state(run)
    integrity(run, state)
    phase = state["phase"]
    if state["status"] != "active" or phase not in PHASES:
        raise ReplayError("run is complete")
    answer_path = Path(answer_file).expanduser().absolute()
    if answer_path.is_symlink() or not answer_path.is_file():
        raise ReplayError(f"answer file must be a regular file: {answer_path}")
    # Reading supplied answers from the run itself would permit accidental context leakage.
    if is_under(answer_path.resolve(), run):
        raise ReplayError("answer file must be outside the run directory")
    answer = validate_answer(safe_json(answer_path), pid, phase)
    rel = f"submissions/{phase}/{pid}.json"
    record_file(run, state, rel, json_bytes(answer))
    (run / MARKER).write_bytes(json_bytes(state))


def submission_paths(run: Path, phase: str) -> dict[str, Path]:
    paths = {}
    for pid in PARTICIPANTS:
        rel = f"submissions/{phase}/{pid}.json"
        path = run / rel
        if not path.is_file():
            raise ReplayError(f"cannot advance: missing {phase} submission from {pid}")
        safe_rel(run, rel)
        paths[pid] = path
    return paths


def advance(run: Path) -> None:
    state = load_state(run)
    integrity(run, state)
    verify_developments(state)
    phase = state["phase"]
    if state["status"] != "active" or phase not in PHASES:
        raise ReplayError("run is complete; it cannot advance again")
    paths = submission_paths(run, phase)
    locked = {pid: {"path": path.relative_to(run).as_posix(), "sha256": digest(path.read_bytes())}
              for pid, path in paths.items()}
    state["locks"].append({"phase": phase, "submissions": locked})
    if phase == "E2":
        state["status"] = "complete"
        state["phase"] = "complete"
        (run / "completion.json").write_bytes(json_bytes({"status": "complete", "locks": state["locks"]}))
        state["files"]["completion.json"] = digest((run / "completion.json").read_bytes())
        (run / MARKER).write_bytes(json_bytes(state))
        return
    event_phase = "E1" if phase == "initial" else "E2"
    next_phase = event_phase
    for scenario in ("carrier", "regression"):
        developments = safe_json(safe_rel(STUDY / "common", f"{scenario}/developments.json"))
        events = developments.get("events", [])
        if scenario == "regression":
            # The frozen packet labels the two releases as stages; normalize only their replay IDs.
            stages = developments.get("stages", [])
            events = [{"id": f"E{i}", "notice": item["message"], "source": item["label"]}
                      for i, item in enumerate(stages[:2], 1)]
        event = next((e for e in events if e.get("id") == event_phase), None)
        if event is None:
            raise ReplayError(f"missing {event_phase} event for {scenario}")
        rel = f"releases/{scenario}/{event_phase}.json"
        record_file(run, state, rel, json_bytes(event))
    # Context for each participant contains only their own earlier submissions and releases.
    for pid, scenario in PARTICIPANTS.items():
        prior = []
        releases = []
        if phase == "initial":
            prior.append({"phase": "initial", "answer": safe_json(paths[pid])})
            releases.append(safe_json(run / f"releases/{scenario}/E1.json"))
        else:  # E1 has now been locked.
            for oldphase in ("initial", "E1"):
                prior.append({"phase": oldphase, "answer": safe_json(run / f"submissions/{oldphase}/{pid}.json")})
                if oldphase == "E1":
                    releases.append(safe_json(run / f"releases/{scenario}/E1.json"))
            releases.append(safe_json(run / f"releases/{scenario}/E2.json"))
        req = request_doc(pid, next_phase, prior, releases)
        record_file(run, state, f"participants/{pid}/{next_phase}-request.json", json_bytes(req))
        msgs = [{"role": "system", "content": req["instructions"]},
                {"role": "user", "content": json.dumps(req, ensure_ascii=False)}]
        record_file(run, state, f"participants/{pid}/{next_phase}-messages.json", json_bytes(msgs))
    state["phase"] = next_phase
    (run / MARKER).write_bytes(json_bytes(state))


def export_research(run: Path) -> None:
    """Copy only specified inputs for 12 pilots and 8 continuation cases."""
    if any(run.iterdir()):
        raise ReplayError("export destination must be empty")
    pilots = sorted((RESEARCH / "pilot").iterdir())
    cases = sorted((RESEARCH / "continuation/cases").iterdir())
    if len(pilots) != 12 or len(cases) != 8:
        raise ReplayError("expected exactly 12 pilot and 8 continuation cases")
    # The explicit allowlist excludes reports, locks, scores, arm maps and analyses.
    names = {"contract.md", "task.md", "prompt.md", "schema.json", "discovery.json",
             "source-checks.json", "frontier.md"}
    for group, dirs in (("pilot", pilots), ("continuation", cases)):
        for case in dirs:
            source_base = case.resolve(strict=True)
            if not is_under(source_base, RESEARCH.resolve()):
                raise ReplayError(f"case escapes research source: {case}")
            rels = {name for name in names if (case / name).is_file()}
            if not {"contract.md", "task.md", "schema.json"}.issubset(rels):
                raise ReplayError(f"required task packet input missing from {group}/{case.name}")
            source_dir = case / "sources"
            if source_dir.exists():
                for f in source_dir.iterdir():
                    if f.suffix.lower() == ".txt" and f.is_file():
                        rels.add(f"sources/{f.name}")
            for rel in sorted(rels):
                src = safe_rel(case, rel)
                dst = run / "research-inputs" / group / case.name / rel
                write_new(dst, src.read_bytes())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare", help="stage the four blinded initial participant packets")
    p.add_argument("--run-dir", required=True)
    p = sub.add_parser("submit", help="validate and record one participant phase response")
    p.add_argument("--run-dir", required=True); p.add_argument("--participant", required=True, choices=PARTICIPANTS)
    p.add_argument("--answer-file", required=True)
    p = sub.add_parser("advance", help="lock all four responses and release the next identical scenario event")
    p.add_argument("--run-dir", required=True)
    p = sub.add_parser("export-research", help="copy only the whitelisted 20 research case inputs")
    p.add_argument("--run-dir", required=True)
    sub.add_parser("verify-publication", help="verify the current public verification manifest")
    args = parser.parse_args(argv)
    try:
        if args.command == "verify-publication":
            verifier_path = REPO / "tools/publish_verification.py"
            spec = importlib.util.spec_from_file_location("publish_verification", verifier_path)
            if spec is None or spec.loader is None:
                raise ReplayError(f"publication verifier unavailable: {verifier_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            summary = module.verify(REPO / "verification")
            print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
            return 0
        if args.command == "prepare":
            run = checked_run_root(args.run_dir, create=True); stage(run)
        elif args.command == "export-research":
            run = checked_run_root(args.run_dir, create=True); export_research(run)
        else:
            run = checked_run_root(args.run_dir)
            if args.command == "submit": submit(run, args.participant, args.answer_file)
            elif args.command == "advance": advance(run)
        print(f"{args.command}: complete ({run})")
        return 0
    except (ReplayError, OSError) as exc:
        print(f"verification_replay: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
