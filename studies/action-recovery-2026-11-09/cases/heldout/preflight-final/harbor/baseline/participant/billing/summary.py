def summarize(rows):
    voided = {row["target"] for row in rows if row["kind"] == "void"}
    totals = {}
    for row in rows:
        if row["kind"] != "charge" or row["billable"] != "1" or row["id"] in voided:
            continue
        group = totals.setdefault(row["account"], {"charge_count": 0, "total_cents": 0})
        group["charge_count"] += 1
        group["total_cents"] += int(row["cents"])
    accounts = [{"account": key, **totals[key]} for key in sorted(totals)]
    return {"currency": "USD", "accounts": accounts,
            "grand_total_cents": sum(group["total_cents"] for group in accounts)}
