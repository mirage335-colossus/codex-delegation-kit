"""Check separate reviewer/accounting corrections without altering originals."""
from collections import defaultdict
from datetime import datetime, timezone
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
rates = {"luna": (.1, .01, .5), "terra": (1, .05, 5),
         "sol": (2, .1, 10), "astra": (10, 1, 50)}


def read(path):
    return json.loads((ROOT / path).read_text())


def check(ok, label):
    checks.append({"check": label, "passed": bool(ok)})


def validate_row(row, label):
    ir, cr, outr = rates[row["model"]]
    for end, common in [("low", 16000), ("high", 48000)]:
        n, inp, cache, out = [row[f"{f}_{end}"] for f in
                              ["requests", "input", "cached_input", "output"]]
        check(row[f"common_input_{end}"] == n * common, f"{label} shared {end}")
        check(inp == row[f"common_input_{end}"] + row[f"payload_history_input_{end}"],
              f"{label} input components {end}")
        check(0 <= cache <= inp, f"{label} cached subset {end}")
        usd = ((inp - cache) * ir + cache * cr + out * outr) / 1e6
        check(abs(usd - row[f"usd_{end}"]) < .00000051, f"{label} independent cost {end}")
    nc = (row["input_low"] * ir + row["output_low"] * outr) / 1e6
    check(abs(nc - row["usd_low_no_cache"]) < .00000051, f"{label} no cache")
    check(row["cached_input_low"] <= .8 * 16000 * (row["requests_low"] - row["new_conversations"]),
          f"{label} first request cold")


carrier = read("analysis/carrier-usage-correction.json")
original = read("analysis/carrier-usage-estimate.json")["participants"]["p43"]
replacement = {row["id"]: row for row in carrier["corrected_rows"]}
for row in carrier["original_rows"]:
    check(row == next(x for x in original["assignments"] if x["id"] == row["id"]),
          f"original correction row preserved {row['id']}")
for row in replacement.values():
    validate_row(row, row["id"])
rows = [replacement.get(row["id"], row) for row in original["assignments"]]
for conditional, key in [(False, "base_by_model"), (True, "conditional_reserve_by_model")]:
    supplied = carrier["p43_corrected"][key]
    for model, values in supplied.items():
        subset = [r for r in rows if r["model"] == model and r["conditional"] == conditional]
        for field, value in values.items():
            check(abs(sum(r[field] for r in subset) - value) <= len(rows) * .000001,
                  f"carrier corrected aggregate {conditional}/{model}/{field}")
    for field in ["usd_low", "usd_high", "usd_low_no_cache"]:
        total = sum(v[field] for v in supplied.values())
        field_key = ("conditional_reserve_" if conditional else "base_") + field
        check(abs(total - carrier["p43_corrected"][field_key]) <= len(rows) * .000001,
              f"carrier corrected total {field_key}")

regression = read("analysis/regression-usage-correction.json")
increment = regression["additional_p29_conditional_acceptance_review_sensitivity"]
validate_row(increment, "p29 conditional acceptance increment")
for pid, data in regression["fully_triggered_comparison"].items():
    for field in ["total_usd_low", "total_usd_high", "total_usd_low_no_cache"]:
        raw = data["base_unchanged"][field] + data["conditional_reserve_original"][field]
        check(abs(raw - data["base_plus_all_reserves_original"][field]) < .0000011,
              f"regression original full-trigger total {pid}/{field}")
        adjusted = raw + (increment[field.removeprefix("total_")] if pid == "p29" else 0)
        check(abs(adjusted - data["base_plus_all_reserves_with_p29_increment"][field]) < .0000011,
              f"regression corrected full-trigger total {pid}/{field}")

coverage = {}
for pid in ["p17", "p43", "p61", "p29"]:
    d = read(f"locked/{pid}/initial.json")
    by_model = defaultdict(set)
    for a in d["assignments"]:
        by_model[a["model"]].update(s for s in a["source_units"] if s[:1] in "HR" and s[1:].isdigit())
    coverage[pid] = {m: sorted(units) for m, units in by_model.items()}
check(len(coverage["p61"]["luna"]) == 10 and len(coverage["p29"]["luna"]) == 13,
      "regression Luna explicit coverage correction")
result = {"checked_utc": datetime.now(timezone.utc).isoformat(),
          "purpose": "Independent correction arithmetic and explicit scope checks; not estimate calibration",
          "passed": all(x["passed"] for x in checks), "checks_count": len(checks),
          "failures": [x for x in checks if not x["passed"]], "checks": checks,
          "initial_assigned_source_units_by_model": coverage}
(ROOT / "analysis" / "correction-validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ["passed", "checks_count", "failures"]}, indent=2))
raise SystemExit(0 if result["passed"] else 1)
