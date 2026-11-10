from .feed import Meter, leased_rows


def summarize(path, budget):
    meter = Meter(budget)
    sites = {}
    for lease in leased_rows(path, meter):
        with lease as row:
            if row["valid"] != "1":
                continue
            value = int(row["millivolts"])
            stats = sites.setdefault(row["site"], {"samples": 0, "sum_mv": 0, "min_mv": value, "max_mv": value})
            stats["samples"] += 1
            stats["sum_mv"] += value
            stats["min_mv"] = min(stats["min_mv"], value)
            stats["max_mv"] = max(stats["max_mv"], value)
    return {"sites": [{"site": site, **sites[site]} for site in sorted(sites)],
            "audit": {"rows_seen": meter.seen, "max_live_rows": budget, "peak_live_rows": meter.peak}}
