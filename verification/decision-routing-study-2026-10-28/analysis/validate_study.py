"""Validate immutable study records and independently recompute usage arithmetic.

This checks accounting, not whether hypothetical campaign estimates are calibrated.
Run from any working directory; it only writes independent-validation.json here.
"""
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
checks = []


def refuse_published_records():
    for path in ROOT.rglob("*.json"):
        try:
            value = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and value.get("publication_scope"):
            print("Historical pre-publication digests are not valid for rewritten artifacts; use the public replay verifier.", file=sys.stderr)
            raise SystemExit(2)


refuse_published_records()


def check(ok, label):
    checks.append({"check": label, "passed": bool(ok)})


def read(path):
    return json.loads((ROOT / path).read_text())


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


frozen = read("input-freeze.json")
for path, expected in frozen["files"].items():
    check(digest(path) == expected, f"frozen input: {path}")
mapping = read("analysis/arm-map.json")
for phase in ["initial", "E1", "E2"]:
    manifest = read(f"locked/{phase}-lock.json")
    complete_key = "all_four_submitted_before_any_estimation" if phase == "E2" else "all_four_submitted_before_release"
    check(manifest[complete_key], f"all four lock: {phase}")
    for path, expected in manifest["files"].items():
        check(digest(path) == expected, f"locked decision: {path}")
        working = path.replace("locked/", "working/", 1)
        check(digest(working) == expected, f"original preserved: {working}")
        check(read(path)["no_tokens_or_costs_estimated"] is True,
              f"decision-only declaration: {path}")
for event, preceding in [("E1", "initial"), ("E2", "E1")]:
    release = read(f"locked/{event}-release.json")
    lock = read(f"locked/{preceding}-lock.json")
    following = read(f"locked/{event}-lock.json")
    check(release["after_lock_sha256"] == digest(f"locked/{preceding}-lock.json"),
          f"{event} refers to preceding lock")
    check(lock["locked_utc"] < release["released_utc"] < following["locked_utc"],
          f"{event} release timestamp ordering")
    for pid, delivery in release["deliveries"].items():
        check(digest(f"views/{pid}/{event}.json") == delivery["sha256"],
              f"delivered bytes: {pid} {event}")
for scenario in ["carrier", "regression"]:
    pids = [p for p, x in mapping.items() if x["scenario"] == scenario]
    for shared in ["scenario.md", "contract.md", "decision-schema.json"]:
        check(digest(f"views/{pids[0]}/{shared}") == digest(f"views/{pids[1]}/{shared}"),
              f"identical {scenario} {shared}")
    for source in (ROOT / "common" / scenario / "sources").glob("*.txt"):
        expected = hashlib.sha256(source.read_bytes()).hexdigest()
        check(all(digest(f"views/{p}/sources/{source.name}") == expected for p in pids),
              f"identical paired source: {scenario} {source.name}")

rates = {"luna": (.10, .01, .50), "terra": (1, .05, 5),
         "sol": (2, .10, 10), "astra": (10, 1, 50)}
numeric = ["requests_low", "requests_high", "input_low", "cached_input_low",
           "output_low", "input_high", "cached_input_high", "output_high",
           "usd_low", "usd_high", "usd_low_no_cache"]
aggregate = {}
for scenario in ["carrier", "regression"]:
    data = read(f"analysis/{scenario}-usage-estimate.json")
    for pid, participant in data["participants"].items():
        stable_ids = set()
        for phase in ["initial", "E1", "E2"]:
            stable_ids.update(a["id"] for a in read(f"locked/{pid}/{phase}.json")["assignments"])
        rows = participant["assignments"]
        ids = [a["id"] for a in rows]
        check(len(ids) == len(set(ids)), f"unique usage rows: {pid}")
        check(stable_ids == {i for i in ids if not i.startswith("ADMIN")},
              f"all stable decisions represented exactly once: {pid}")
        summed = {False: defaultdict(lambda: defaultdict(float)),
                  True: defaultdict(lambda: defaultdict(float))}
        for row in rows:
            label = f"{pid}/{row['id']}"
            ir, cr, outr = rates[row["model"]]
            for endpoint, common in [("low", 16000), ("high", 48000)]:
                count, inp, cache, out = [row[f"{k}_{endpoint}"] for k in
                                          ["requests", "input", "cached_input", "output"]]
                check(0 <= cache <= inp and count > 0 and out >= 0,
                      f"valid bounds: {label}/{endpoint}")
                check(row[f"common_input_{endpoint}"] == common * count,
                      f"shared input component: {label}/{endpoint}")
                check(inp == row[f"common_input_{endpoint}"] + row[f"payload_history_input_{endpoint}"],
                      f"input component sum: {label}/{endpoint}")
                computed = ((inp - cache) * ir + cache * cr + out * outr) / 1e6
                check(abs(computed - row[f"usd_{endpoint}"]) <= .00000051,
                      f"independent cost: {label}/{endpoint}")
            check(row["requests_low"] <= row["requests_high"] and row["input_low"] <= row["input_high"],
                  f"ordered endpoints: {label}")
            check(row["cached_input_high"] == 0, f"cold high endpoint: {label}")
            new = row.get("new_conversations", 0)
            check(row["cached_input_low"] <= .8 * 16000 * (row["requests_low"] - new),
                  f"no cache on first request: {label}")
            no_cache = (row["input_low"] * ir + row["output_low"] * outr) / 1e6
            check(abs(no_cache - row["usd_low_no_cache"]) <= .00000051,
                  f"independent no-cache cost: {label}")
            for field in numeric:
                summed[row["conditional"]][row["model"]][field] += row[field]
        conditional = participant.get("conditional_reserve", {})
        reserves = participant.get("conditional_reserve_by_model", conditional.get("totals_by_model", {}))
        for flag, supplied in [(False, participant["totals_by_model"]), (True, reserves)]:
            check(set(supplied) == set(summed[flag]), f"model inventory base/reserve {pid}/{flag}")
            for model, values in supplied.items():
                for field in numeric:
                    tolerance = len(rows) * .000001 if field.startswith("usd") else 0
                    check(abs(values[field] - summed[flag][model][field]) <= tolerance,
                          f"model aggregate {pid}/{flag}/{model}/{field}")
            for field in ["usd_low", "usd_high", "usd_low_no_cache"]:
                expected = sum(x[field] for x in summed[flag].values())
                key = ("conditional_reserve_" if flag and scenario == "carrier" else "total_") + field
                actual = participant[key] if not flag or scenario == "carrier" else conditional[key]
                check(abs(expected - actual) <= len(rows) * .000001,
                      f"total aggregate {pid}/{flag}/{field}")
        aggregate[pid] = {"base": participant["totals_by_model"], "reserve": reserves}

result = {
    "checked_utc": datetime.now(timezone.utc).isoformat(),
    "purpose": "Independent hash, equality, lock-order, structural and arithmetic checks; no calibration or provider identity proof",
    "passed": all(c["passed"] for c in checks),
    "checks_count": len(checks),
    "failures": [c for c in checks if not c["passed"]],
    "checks": checks,
    "rates_usd_per_million_input_cached_output": rates,
    "recomputed_aggregates": aggregate,
}
(ROOT / "analysis" / "independent-validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ["passed", "checks_count", "failures"]}, indent=2))
raise SystemExit(0 if result["passed"] else 1)
