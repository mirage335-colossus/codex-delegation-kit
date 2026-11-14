#!/usr/bin/env python3
"""Inventory study artifacts and check local integrity bookkeeping.

This stdlib-only report deliberately treats prose classes separately. It does
not claim that a file count, word count, receipt, or hash establishes science
quality, unmetered activity, source access, or compliance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
REPORTS = {"evaluation/integrity-preliminary.json", "evaluation/integrity-preliminary.md",
           "evaluation/integrity-final.json", "evaluation/integrity-final.md"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\((<[^>]*>|[^\s)]*(?:\s+['\"][^)]*['\"])?\s*)\)")
REF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE)
FENCE_RE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
TIMESTAMP_NAME_RE = re.compile(r"(?:time|date|timestamp|created|finished|updated|late)", re.I)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def prose_class(rel: str) -> str:
    p = Path(rel)
    if p.parts[0] == "evaluation":
        return "evaluator"
    name = p.name.lower()
    if re.search(r"(?:first-pass|initial|correction|corrections|correction-pass)", name):
        return "historical-first-pass-or-correction"
    if p.parts[0] == "research" and name in {"chapter.md", "source-ledger.md", "synthesis.md"}:
        return "current-scientific-prose"
    if p.parts[0] == "research" and (name.startswith("chapter-continuation") or name.startswith("source-ledger-continuation")):
        return "supplemental-continuation-prose"
    return "other-study-markdown"


def link_provenance(rel: str) -> str:
    parts = Path(rel).parts
    name = Path(rel).name.lower()
    if "first-pass" in parts or "interim-synthesis" in parts or "snapshot" in name:
        return "historical-first-pass-or-interim-snapshot"
    if "reviews" in parts or parts[0] == "research":
        return "active-review-or-current-research"
    return "other-study-source"


def inventory(root: Path) -> list[dict]:
    records = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel in REPORTS or path.is_dir():
            continue
        try:
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                records.append({"path": rel, "kind": "symlink", "size_bytes": None,
                                "sha256": None, "note": "not followed"})
            elif stat.S_ISREG(mode):
                records.append({"path": rel, "kind": "file", "size_bytes": path.stat().st_size,
                                "sha256": sha256(path)})
            else:
                records.append({"path": rel, "kind": "special", "size_bytes": None,
                                "sha256": None})
        except OSError as exc:
            records.append({"path": rel, "kind": "unreadable", "size_bytes": None,
                            "sha256": None, "error": str(exc)})
    return records


def markdown_links(root: Path, md_paths: list[Path]) -> dict:
    checked, missing, skipped = [], [], []
    root_abs = Path(os.path.abspath(root))
    for source in md_paths:
        text = source.read_text(encoding="utf-8", errors="replace")
        text = FENCE_RE.sub("", text)
        targets = [m.group(1).strip() for m in LINK_RE.finditer(text)]
        targets.extend(m.group(1).strip() for m in REF_RE.finditer(text))
        for raw in targets:
            target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
            target = target.split()[0] if target else ""
            if not target or target.startswith("#"):
                continue
            # Codex local links may append :line (and optionally :column).
            path_target = re.sub(r":\d+(?::\d+)?$", "", target) if "://" not in target else target
            parsed = urlsplit(path_target)
            if parsed.scheme or parsed.netloc:
                continue
            file_part = unquote(parsed.path)
            if not file_part:
                continue
            candidate = Path(os.path.abspath(source.parent / file_part)) if not file_part.startswith("/") else Path(os.path.abspath(file_part))
            try:
                rel = candidate.relative_to(root_abs).as_posix()
            except ValueError:
                skipped.append({"source": source.relative_to(root).as_posix(), "target": target,
                                "reason": "resolves outside study scope; not inspected"})
                continue
            # lstat each component so no symlink, including an outward-pointing
            # symlink, is followed during the existence check.
            current = root_abs
            found = True
            symlink = False
            for part in Path(rel).parts:
                current = current / part
                try:
                    mode = current.lstat().st_mode
                except FileNotFoundError:
                    found = False
                    break
                except OSError:
                    found = False
                    break
                if stat.S_ISLNK(mode):
                    symlink = True
                    break
            item = {"source": source.relative_to(root).as_posix(), "target": target,
                    "source_provenance": link_provenance(source.relative_to(root).as_posix())}
            if symlink:
                skipped.append({**item, "reason": "symlink encountered; not followed"})
            elif not found:
                missing.append(item)
            else:
                checked.append(item)
    active_missing = [x for x in missing if x.get("source_provenance") == "active-review-or-current-research"]
    historical_missing = [x for x in missing if x.get("source_provenance") == "historical-first-pass-or-interim-snapshot"]
    return {"checked_count": len(checked), "checked": checked,
            "missing_count": len(missing), "missing": missing,
            "active_missing_count": len(active_missing), "active_missing": active_missing,
            "historical_missing_count": len(historical_missing), "historical_missing": historical_missing,
            "skipped_count": len(skipped), "skipped": skipped,
            "method_limit": "Inline and reference-style Markdown paths only; Codex :line/:column suffixes are removed for file existence checks, not validated as positions. Fenced code, HTML links, and links outside this study are not inspected."}


def meter_check(root: Path) -> dict:
    meter_path = root / "meter.json"
    allocations_path = root / "allocations.json"
    meter = json.loads(meter_path.read_text(encoding="utf-8"))
    allocations = json.loads(allocations_path.read_text(encoding="utf-8"))
    ids = meter.get("receipts", [])
    errors, statuses = [], Counter()
    op_by_run, receipt_count_by_run = Counter(), Counter()
    metadata_keys, timestamp_fields, missing, extras = Counter(), [], [], []
    listed = set(ids)
    receipt_dir = root / "receipts"
    actual_files = {p.stem for p in receipt_dir.glob("*.json")}
    extras = sorted(actual_files - listed)
    for rid in ids:
        path = receipt_dir / f"{rid}.json"
        if not path.is_file():
            missing.append(rid)
            continue
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({"id": rid, "error": str(exc)})
            continue
        run, operations, status = receipt.get("run"), receipt.get("operations"), receipt.get("status")
        statuses[status] += 1
        if not isinstance(run, str) or not isinstance(operations, int) or isinstance(operations, bool) or operations < 0:
            errors.append({"id": rid, "error": "missing or invalid run/operations"})
            continue
        op_by_run[run] += operations
        receipt_count_by_run[run] += 1
        if receipt.get("id") != rid:
            errors.append({"id": rid, "error": "receipt id field does not match filename/list"})
        for key in receipt:
            metadata_keys[key] += 1
            if TIMESTAMP_NAME_RE.search(key):
                timestamp_fields.append(f"{rid}:{key}")
        result = receipt.get("result")
        if isinstance(result, dict):
            for key in result:
                if TIMESTAMP_NAME_RE.search(key):
                    timestamp_fields.append(f"{rid}:result.{key}")
        elif result is not None:
            errors.append({"id": rid, "error": "result metadata is not an object"})
    used = meter.get("used", {})
    runs = sorted(set(used) | set(op_by_run))
    run_checks = []
    for run in runs:
        recorded = used.get(run, 0)
        calculated = op_by_run.get(run, 0)
        cap = allocations.get("runs", {}).get(run)
        run_checks.append({"run": run, "meter_used": recorded, "receipt_operations": calculated,
                           "cap": cap, "count_matches": recorded == calculated,
                           "within_cap": isinstance(cap, int) and recorded <= cap})
    total_used = sum(used.values()) if all(isinstance(v, int) for v in used.values()) else None
    incident = root / "evaluation/boundary-incident.md"
    incident_text = incident.read_text(encoding="utf-8", errors="replace") if incident.is_file() else ""
    manual_uncertainty_headings = []
    for heading in re.findall(r"^##\s+(.+)$", incident_text, re.MULTILINE):
        if re.search(r"uncertaint|unknown|late|continuation", heading, re.I):
            manual_uncertainty_headings.append(heading)
    return {
        "meter_version": meter.get("version"), "receipt_id_count": len(ids),
        "receipt_file_count": len(actual_files), "statuses": dict(sorted(statuses.items())),
        "unfinished_ids": sorted(rid for rid in ids if (receipt_dir / f"{rid}.json").is_file()
                                 and json.loads((receipt_dir / f"{rid}.json").read_text(encoding="utf-8")).get("status") == "reserved"),
        "missing_receipt_ids": missing, "unlisted_receipt_files": extras,
        "metadata_fields": dict(sorted(metadata_keys.items())), "timestamp_or_late_fields": sorted(set(timestamp_fields)),
        "timestamp_or_late_fields_present": bool(timestamp_fields),
        "timing_reconstructable": False,
        "late_recording_limit": "No trusted receipt/call timestamps are present; lateness cannot be independently inferred from this meter.",
        "documented_manual_or_timing_uncertainty_sections": manual_uncertainty_headings,
        "manual_activity_limit": "Receipts cover cooperative wrapped operations only. Boundary-incident reports manual source-call uncertainty and a late groundwave reservation; neither can be certified or cleared by aggregate receipt consistency.",
        "run_checks": run_checks, "total_cap": allocations.get("total_cap"),
        "meter_total_used": total_used, "receipt_total_operations": sum(op_by_run.values()),
        "total_within_cap": isinstance(total_used, int) and total_used <= allocations.get("total_cap", -1),
        "errors": errors,
    }


def freeze_check(root: Path) -> dict:
    frozen = json.loads((root / "prospective-freeze.json").read_text(encoding="utf-8"))
    checks = []
    for rel, expected in sorted(frozen.get("files", {}).items()):
        path = root / rel
        actual = sha256(path) if path.is_file() else None
        checks.append({"path": rel, "expected_sha256": expected, "actual_sha256": actual,
                       "matches": actual == expected})
    uptake_path = root / "evaluation/uptake-design/freeze.sha256"
    uptake = []
    for line in uptake_path.read_text(encoding="utf-8").splitlines():
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        expected, rel = parts[0], parts[1].lstrip("* ")
        path = root / "evaluation/uptake-design" / rel
        actual = sha256(path) if path.is_file() else None
        uptake.append({"path": path.relative_to(root).as_posix(), "expected_sha256": expected,
                       "actual_sha256": actual, "matches": actual == expected})
    science = []
    science_path = root / "evaluation/science-freeze.json"
    if science_path.is_file():
        final_inputs = json.loads(science_path.read_text(encoding="utf-8"))
        for rel, expected in sorted(final_inputs.get("files", {}).items()):
            path = root / rel
            actual = sha256(path) if path.is_file() else None
            science.append({"path": rel, "expected_sha256": expected,
                            "actual_sha256": actual, "matches": actual == expected})
    corpus = json.loads((root / "evaluation/corpus-inventory.json").read_text(encoding="utf-8"))
    return {"prospective_stage": frozen.get("stage"), "prospective_files": checks,
            "uptake_frozen_files": uptake,
            "final_science_and_uptake_inputs": science,
            "all_frozen_hashes_match": all(x["matches"] for x in checks + uptake + science),
            "recorded_comparator_source_ids": {k: corpus.get(k) for k in ("kit_head", "pump_head")},
            "comparator_source_identity_limit": "These IDs are recorded in the original inventory. This tool does not inspect pump source or verify the historical repository states."}


def git_trackability(root: Path) -> dict:
    try:
        top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                             check=True, capture_output=True, text=True).stdout.strip()
        repo = Path(top).resolve()
        rel_root = root.relative_to(repo).as_posix()
        tracked_raw = subprocess.run(["git", "-C", str(repo), "ls-files", "-z", "--", rel_root],
                                     check=True, capture_output=True).stdout
        status = subprocess.run(["git", "-C", str(repo), "status", "--short", "--untracked-files=all", "--", rel_root],
                                check=True, capture_output=True, text=True).stdout.splitlines()
        tracked = [x for x in tracked_raw.decode("utf-8", errors="replace").split("\0") if x]
        untracked = [line[3:] for line in status if line.startswith("?? ")]
        return {"git_available": True, "tracked_path_count": len(tracked),
                "untracked_path_count": len(untracked), "untracked_paths": untracked,
                "recommendation": "Review untracked source/evidence for intended durable inclusion. Retain reproducibility-critical receipts and logs; classify scratch/tmp outputs, compiled binaries, and bytecode caches before staging or excluding them. This report deletes nothing."}
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        return {"git_available": False, "error": str(exc),
                "recommendation": "Check Git tracking status manually; no files were changed or deleted."}


def build_report(root: Path) -> dict:
    root = root.resolve()
    files = inventory(root)
    md_paths = sorted(p for p in root.rglob("*.md") if p.relative_to(root).as_posix() not in REPORTS and p.is_file())
    classes = Counter()
    prose = []
    for path in md_paths:
        rel = path.relative_to(root).as_posix()
        cls = prose_class(rel)
        classes[cls] += 1
        prose.append({"path": rel, "class": cls, "words": word_count(path.read_text(encoding="utf-8", errors="replace"))})
    suffix_sizes = defaultdict(lambda: {"count": 0, "bytes": 0})
    for item in files:
        suffix = Path(item["path"]).suffix.lower() or "[no extension]"
        suffix_sizes[suffix]["count"] += 1
        if item.get("size_bytes") is not None:
            suffix_sizes[suffix]["bytes"] += item["size_bytes"]
    largest = sorted((x for x in files if x.get("size_bytes") is not None),
                     key=lambda x: (-x["size_bytes"], x["path"]))[:20]
    artifacts = [x["path"] for x in files if ("__pycache__" in x["path"].split("/") or
                 x["path"].endswith((".tmp", ".pyc")) or "/tmp/" in x["path"])]
    links = markdown_links(root, md_paths)
    return {"scope": root.name, "inventory_note": "Hashes and sizes cover regular study files, excluding generated preliminary/final integrity reports to avoid self-reference. Symlinks are listed but never followed.",
            "file_count": len(files), "total_regular_file_bytes": sum(x["size_bytes"] or 0 for x in files),
            "files": files, "suffix_summary": dict(sorted(suffix_sizes.items())),
            "largest_files": largest, "generated_cache_or_temporary_candidates": artifacts,
            "prose_classification_rule": {
                "current-scientific-prose": "research/** chapter.md, source-ledger.md, synthesis.md; canonical active files only.",
                "historical-first-pass-or-correction": "Research Markdown whose basename explicitly marks first-pass, initial, or correction material.",
                "supplemental-continuation-prose": "Research Markdown named chapter-continuation* or source-ledger-continuation*.",
                "evaluator": "All evaluation/** Markdown, including interim synthesis, maps, criteria, and adjudication.",
                "other-study-markdown": "Remaining Markdown; not presumed to be scientific prose."},
            "prose_file_counts_by_class": dict(sorted(classes.items())),
            "prose_files": prose,
            "word_count_note": "Per-file whitespace-token counts only; no aggregate word total is reported because chapters, ledgers, synthesis, and historical/evaluator text overlap in purpose.",
            "trackability": git_trackability(root),
            "markdown_local_links": links, "meter": meter_check(root), "freeze_and_identity": freeze_check(root)}


def markdown_summary(report: dict) -> str:
    meter = report["meter"]
    freeze = report["freeze_and_identity"]
    lines = ["# Study integrity inventory", "",
             f"Inventory: {report['file_count']} files, {report['total_regular_file_bytes']} regular-file bytes. The JSON report contains per-file sizes and SHA-256 hashes.",
             "",
             "## Prose classification", "",
             "Current canonical scientific chapters, ledgers, and synthesis are classified separately from explicitly named first-pass/correction records, continuation prose, evaluator Markdown, and other Markdown. The JSON lists per-file word counts only; no cross-category aggregate is given.", "",
             "File counts by class: " + ", ".join(f"{k}: {v}" for k, v in report["prose_file_counts_by_class"].items()) + ". Individual per-file word counts are in JSON; these are separate measures.", "",
             "## Integrity checks", "",
             f"- Markdown links: {report['markdown_local_links']['checked_count']} local paths checked; {report['markdown_local_links']['missing_count']} missing; {report['markdown_local_links']['skipped_count']} outside-scope or symlink paths skipped.",
             f"- Meter: {meter['receipt_id_count']} listed receipts, statuses {meter['statuses']}; {len(meter['unfinished_ids'])} unfinished; {len(meter['missing_receipt_ids'])} missing and {len(meter['unlisted_receipt_files'])} unlisted receipt files.",
             f"- Meter operation totals: {meter['receipt_total_operations']} in receipts vs {meter['meter_total_used']} in meter; total cap {meter['total_cap']}, within cap: {meter['total_within_cap']}. Per-run details are in JSON.",
             f"- Timestamp/late-recording fields found: {len(meter['timestamp_or_late_fields'])}; timing reconstructable: {meter['timing_reconstructable']}. {meter['late_recording_limit']}",
             f"- Manual/timing caveat: {meter['manual_activity_limit']} Relevant incident sections: {', '.join(meter['documented_manual_or_timing_uncertainty_sections'])}.",
             f"- Prospective and uptake frozen hashes match: {freeze['all_frozen_hashes_match']}.",
             "- Comparator kit/pump source IDs are reproduced from corpus-inventory.json, not independently validated. Pump source and appraisal files were not opened.",
             f"- Missing links include {report['markdown_local_links']['active_missing_count']} from active research/review sources and {report['markdown_local_links']['historical_missing_count']} from first-pass/interim snapshots. Historical text is left intact; any active missing paths should be repaired before final freeze.",
             "",
             "## Artifact handling", "",
             "See the JSON for largest files, cache/temporary candidates, suffix counts, and Git tracking status. Review untracked source/evidence for intended durable inclusion; retain reproducibility-critical receipts and logs, and classify scratch/tmp outputs, compiled binaries, and bytecode caches before staging or excluding them. The inventory deletes nothing.", "",
             "## Limits", "",
             "The cooperative meter observes wrapped web operations only. These checks cannot prove manual/unwrapped calls, timely receipt creation, source-reading depth, participant compliance, or scientific acceptance. The historical pump dirty-state string contains paths in restricted comparator locations; it is treated as recorded metadata only.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--json-output", type=Path, default=None)
    parser.add_argument("--markdown-output", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    report = build_report(root)
    json_path = args.json_output or root / "evaluation/integrity-preliminary.json"
    md_path = args.markdown_output or root / "evaluation/integrity-preliminary.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(markdown_summary(report), encoding="utf-8")
    print(json.dumps({"files": report["file_count"], "bytes": report["total_regular_file_bytes"],
                      "prose_file_counts": report["prose_file_counts_by_class"],
                      "missing_links": report["markdown_local_links"]["missing_count"],
                      "meter_consistent": all(x["count_matches"] for x in report["meter"]["run_checks"]),
                      "unfinished_receipts": len(report["meter"]["unfinished_ids"]),
                      "frozen_hashes_match": report["freeze_and_identity"]["all_frozen_hashes_match"],
                      "outputs": [str(json_path), str(md_path)]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
