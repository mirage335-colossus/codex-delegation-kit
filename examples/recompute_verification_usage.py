#!/usr/bin/env python3
"""Recompute descriptive token totals from the published verification JSONL."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


DATASET = (
    Path(__file__).resolve().parents[1]
    / "verification"
    / "telemetry"
    / "usage-records.jsonl"
)
METRICS = (
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)
FIELDS = {
    "cohort",
    "role",
    "model",
    "participant",
    "attempt",
    "response",
    *METRICS,
}
COHORTS = ("earlier", "latest")
ROLES = ("delegated", "main_chat")


def _validate_record(record: Any, line_number: int) -> dict[str, Any]:
    prefix = f"line {line_number}"
    if not isinstance(record, dict):
        raise ValueError(f"{prefix}: expected a JSON object")
    if set(record) != FIELDS:
        missing = sorted(FIELDS - set(record))
        extra = sorted(set(record) - FIELDS)
        raise ValueError(f"{prefix}: field mismatch (missing={missing}, extra={extra})")
    for key in ("cohort", "role", "model", "participant", "attempt", "response"):
        value = record[key]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{prefix}: {key} must be a nonempty string")
    if record["cohort"] not in COHORTS:
        raise ValueError(f"{prefix}: unsupported cohort {record['cohort']!r}")
    if record["role"] not in ROLES:
        raise ValueError(f"{prefix}: unsupported role {record['role']!r}")

    for key in METRICS:
        value = record[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{prefix}: {key} must be a finite nonnegative number")
        if not math.isfinite(value) or value < 0 or not float(value).is_integer():
            raise ValueError(f"{prefix}: {key} must be a finite nonnegative integer")
    if record["cached_input_tokens"] > record["input_tokens"]:
        raise ValueError(f"{prefix}: cached input cannot exceed input")
    if record["reasoning_output_tokens"] > record["output_tokens"]:
        raise ValueError(f"{prefix}: reasoning output cannot exceed output")
    if record["total_tokens"] != record["input_tokens"] + record["output_tokens"]:
        raise ValueError(f"{prefix}: total must equal input plus output")
    return record


def read_records(path: Path) -> list[dict[str, Any]]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result
    records = []
    seen = set()
    try:
        stream = path.open(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"cannot read input dataset: {exc}") from exc
    with stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                raise ValueError(f"line {line_number}: blank lines are not allowed")
            try:
                raw = json.loads(line, object_pairs_hook=unique_object, parse_constant=lambda token: (_ for _ in ()).throw(
                    ValueError(f"non-finite JSON constant {token}")))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"line {line_number}: invalid JSON ({exc})") from exc
            record = _validate_record(raw, line_number)
            key = (record["cohort"], record["participant"], record["response"])
            if key in seen:
                raise ValueError(f"line {line_number}: duplicate public response key")
            seen.add(key)
            records.append(record)
    if not records:
        raise ValueError("input dataset contains no records")
    return records


def _aggregate(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(records)
    totals = {metric: sum(row[metric] for row in rows) for metric in METRICS}
    return {
        "records": len(rows),
        "participants": len({row["participant"] for row in rows}),
        "attempts": len({(row["participant"], row["attempt"]) for row in rows}),
        **totals,
    }


def _luna_shares(records: list[dict[str, Any]]) -> dict[str, Any]:
    shares = {}
    for scope, scoped_rows in (
        ("all_records", records),
        ("delegated", [row for row in records if row["role"] == "delegated"]),
    ):
        luna_rows = [row for row in scoped_rows if row["model"] == "gpt-6-luna"]
        totals = _aggregate(scoped_rows)
        luna_totals = _aggregate(luna_rows)
        shares[scope] = {
            metric: (luna_totals[metric] / totals[metric] if totals[metric] else None)
            for metric in ("input_tokens", "output_tokens", "total_tokens")
        }
    return shares


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_cohort: dict[str, Any] = {}
    for cohort in COHORTS:
        cohort_rows = [row for row in records if row["cohort"] == cohort]
        by_role: dict[str, Any] = {}
        for role in ROLES:
            role_rows = [row for row in cohort_rows if row["role"] == role]
            by_model = {
                model: _aggregate(row for row in role_rows if row["model"] == model)
                for model in sorted({row["model"] for row in role_rows})
            }
            by_role[role] = {"totals": _aggregate(role_rows), "by_model": by_model}
        by_cohort[cohort] = {
            "totals": _aggregate(cohort_rows),
            "by_role": by_role,
            "luna_share": _luna_shares(cohort_rows),
        }

    combined_by_model: dict[str, Any] = {}
    for model in sorted({row["model"] for row in records}):
        model_rows = [row for row in records if row["model"] == model]
        combined_by_model[model] = {
            "totals": _aggregate(model_rows),
            "by_role": {
                role: _aggregate(row for row in model_rows if row["role"] == role)
                for role in ROLES
                if any(row["role"] == role for row in model_rows)
            },
        }

    return {
        "records": len(records),
        "by_cohort": by_cohort,
        "combined_by_model": combined_by_model,
        "luna_share": _luna_shares(records),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DATASET, help="JSONL input (default: bundled dataset)")
    parser.add_argument("--output", type=Path, help="write JSON summary here (default: stdout)")
    args = parser.parse_args(argv)
    try:
        result = summarize(read_records(args.input))
        rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
