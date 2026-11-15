#!/usr/bin/env python3
"""Validate and summarize post-lock scientific dispositions without regrading.

Exit 0 means structurally complete aggregation, even when readiness is false.
Exit 2 means invalid/missing input or an output refusal. The output must not
exist and its parent must exist. Reviews and the matrix are never modified.
Hashes identify the bytes read; this tool does not establish a submission lock,
verify evidence/conditional applicability, or assess scientific adequacy.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


SUPPORTED = {"Supported", "Supported boundary"}
OUTSIDE = "Outside declared conditions"
DISPOSITIONS = SUPPORTED | {"Partial", "Unsupported", OUTSIDE}
DEPTH_IDS = set(range(1, 7))


class ReviewError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReviewError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ReviewError(f"nonfinite JSON constant: {value}")


def load(path, receipt):
    require(not any(p.is_symlink() for p in (path, *path.parents)),
            f"symlink input is not supported: {path}")
    raw = path.read_bytes()
    receipt["sha256"] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def string_list(value):
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def matrix_domains(matrix):
    require(isinstance(matrix, dict), "matrix must be an object")
    domains = matrix.get("domains")
    require(isinstance(domains, list) and domains, "matrix needs nonempty domains")
    expected, all_rows = {}, set()
    for domain in domains:
        require(isinstance(domain, dict), "matrix domain must be an object")
        identity = domain.get("domain_id")
        require(text(identity), "matrix domain_id must be nonempty text")
        require(identity not in expected, f"duplicate matrix domain_id: {identity}")
        criteria = domain.get("criteria")
        require(isinstance(criteria, list) and criteria,
                f"{identity}: matrix criteria must be nonempty")
        rows = {}
        for row in criteria:
            require(isinstance(row, dict), f"{identity}: matrix row must be an object")
            row_id, applicability = row.get("id"), row.get("applicability")
            require(text(row_id), f"{identity}: matrix row id must be nonempty text")
            require(row_id not in all_rows, f"duplicate matrix row id: {row_id}")
            require(applicability in ("essential", "scoped_conditional"),
                    f"{row_id}: unknown matrix applicability {applicability!r}")
            all_rows.add(row_id)
            rows[row_id] = applicability
        expected[identity] = rows
    return expected


def exact_items(items, key, expected, label, integer=False):
    require(isinstance(items, list), f"{label} must be an array")
    found = {}
    for item in items:
        require(isinstance(item, dict), f"{label} item must be an object")
        identity = item.get(key)
        require(type(identity) is int if integer else text(identity),
                f"{label}: invalid {key}: {identity!r}")
        require(identity not in found, f"{label}: duplicate {key}: {identity}")
        found[identity] = item
    missing, extra = set(expected) - set(found), set(found) - set(expected)
    require(not missing and not extra,
            f"{label}: missing {sorted(missing)}, extra {sorted(extra)}")
    return found


def validate_review(review, expected):
    require(isinstance(review, dict), "review must be an object")
    domain = review.get("domain_id")
    require(text(domain) and domain in expected, f"unexpected domain_id: {domain!r}")
    overall = review.get("overall")
    require(isinstance(overall, str) and overall in DISPOSITIONS - {OUTSIDE},
            f"{domain}: invalid overall disposition {overall!r}")
    for field in ("source_access_limits", "executed_checks", "unexecuted_checks", "resource_notes"):
        require(string_list(review.get(field)), f"{domain}: {field} must be a string array")
    rows = exact_items(review.get("rows"), "id", expected[domain], f"{domain} rows")
    depths = exact_items(review.get("depth_checks"), "number", DEPTH_IDS,
                         f"{domain} depth_checks", integer=True)
    for identity, row in rows.items():
        disposition = row.get("disposition")
        require(isinstance(disposition, str) and disposition in DISPOSITIONS,
                f"{identity}: invalid disposition {disposition!r}")
        require(disposition != OUTSIDE or expected[domain][identity] == "scoped_conditional",
                f"{identity}: essential row cannot be {OUTSIDE}")
        require(text(row.get("reason")), f"{identity}: reason must be nonempty text")
        for field in ("participant_evidence", "independent_checks"):
            require(string_list(row.get(field)), f"{identity}: {field} must be a string array")
        require("remaining_action" in row and (row["remaining_action"] is None
                or isinstance(row["remaining_action"], str)),
                f"{identity}: remaining_action must be text or null")
    for number, depth in depths.items():
        disposition = depth.get("disposition")
        require(isinstance(disposition, str) and disposition in DISPOSITIONS - {OUTSIDE},
                f"{domain} depth {number}: invalid disposition {disposition!r}")
        require(text(depth.get("reason")) and string_list(depth.get("evidence")),
                f"{domain} depth {number}: reason/evidence have invalid shape")
    unmet_rows = sorted(identity for identity, row in rows.items()
                        if row["disposition"] not in SUPPORTED | {OUTSIDE})
    unmet_depth = sorted(number for number, depth in depths.items()
                         if depth["disposition"] not in SUPPORTED)
    ready = not unmet_rows and not unmet_depth
    return {
        "domain_id": domain, "author_overall": overall,
        "derived_ready": ready,
        "author_derived_readiness_agree": (overall in SUPPORTED) == ready,
        "all_essential_and_applicable_rows_ready": not unmet_rows,
        "all_depth_checks_ready": not unmet_depth,
        "unmet_row_ids": unmet_rows, "unmet_depth_ids": unmet_depth,
        "outside_conditional_row_ids": sorted(identity for identity, row in rows.items()
                                               if row["disposition"] == OUTSIDE),
        "row_counts": dict(sorted(Counter(row["disposition"] for row in rows.values()).items())),
        "depth_counts": dict(sorted(Counter(depth["disposition"] for depth in depths.values()).items())),
    }


def aggregate(matrix_path, reviews_path):
    result = {
        "version": 1, "validation_status": "invalid", "derived_ready": False,
        "matrix": {"artifact": str(matrix_path), "sha256": None},
        "reviews_directory": str(reviews_path), "inputs": [], "domains": [],
        "errors": [], "missing_domain_ids": [], "duplicate_domain_ids": [],
        "summary_limit": "Counts summarize labels; no averaging or scientific regrading. "
                         "Outside dispositions establish only reviewer-declared conditional scope. "
                         "Input hashes do not prove a lock or source/evidence validity.",
    }
    try:
        expected = matrix_domains(load(matrix_path, result["matrix"]))
    except (OSError, ValueError) as exc:
        result["errors"].append(f"matrix: {exc}")
        return result
    result["expected_domain_ids"] = sorted(expected)
    seen = Counter()
    try:
        require(reviews_path.is_dir(), f"reviews directory does not exist: {reviews_path}")
        require(not any(p.is_symlink() for p in (reviews_path, *reviews_path.parents)),
                "reviews directory must not traverse symlinks")
        paths = sorted(reviews_path.rglob("dispositions.json"))
        for path in paths:
            receipt = {"artifact": str(path), "sha256": None}
            result["inputs"].append(receipt)
            try:
                review = load(path, receipt)
                # Count identifiable submitted domains even if their contents fail validation.
                if isinstance(review, dict) and text(review.get("domain_id")):
                    seen[review["domain_id"]] += 1
                summary = validate_review(review, expected)
                result["domains"].append({**summary, **receipt})
            except (OSError, ValueError) as exc:
                result["errors"].append(f"{path}: {exc}")
    except (OSError, ValueError) as exc:
        result["errors"].append(str(exc))
    result["missing_domain_ids"] = sorted(set(expected) - set(seen))
    result["duplicate_domain_ids"] = sorted(domain for domain, count in seen.items() if count > 1)
    if result["missing_domain_ids"]:
        result["errors"].append(f"missing reviewer domains: {result['missing_domain_ids']}")
    if result["duplicate_domain_ids"]:
        result["errors"].append(f"duplicate reviewer domains: {result['duplicate_domain_ids']}")
    result["domains"].sort(key=lambda item: (item["domain_id"], item["artifact"]))
    for field in ("row_counts", "depth_counts"):
        counts = Counter()
        for domain in result["domains"]:
            counts.update(domain[field])
        result[field] = dict(sorted(counts.items()))
    result["counts_scope"] = "Structurally valid review files only; duplicates remain visible if validation fails."
    if not result["errors"]:
        result["validation_status"] = "complete"
        result["derived_ready"] = all(domain["derived_ready"] for domain in result["domains"])
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        require(not args.output.resolve().is_relative_to(args.reviews.resolve()),
                "output must be outside the source reviews directory")
        require(not args.output.exists() and not args.output.is_symlink(),
                f"output already exists: {args.output}")
        result = aggregate(args.matrix.absolute(), args.reviews.absolute())
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        print(json.dumps({"output": str(args.output), "validation_status": result["validation_status"],
                          "derived_ready": result["derived_ready"], "errors": result["errors"]}))
        return 0 if result["validation_status"] == "complete" else 2
    except (OSError, ValueError) as exc:
        print(json.dumps({"validation_status": "invalid", "derived_ready": False,
                          "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
