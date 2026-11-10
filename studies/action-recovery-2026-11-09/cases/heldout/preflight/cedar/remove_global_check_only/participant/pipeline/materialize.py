"""CSV transformations shared by the nightly pipeline."""
import csv
from pathlib import Path


def read_rows(path):
    with Path(path).open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path, fields, rows):
    with Path(path).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def materialize(job, root, state):
    destination = state / (job["id"] + ".csv")
    if job["kind"] == "stock":
        totals = {}
        for row in read_rows(root / job["inputs"][0]):
            totals[row["sku"]] = totals.get(row["sku"], 0) + int(row["units"])
        write_rows(destination, ["sku", "units"],
                   [{"sku": sku, "units": totals[sku]} for sku in sorted(totals)])
    elif job["kind"] == "prices":
        catalog = {row["sku"]: int(row["cents"]) for row in read_rows(root / job["inputs"][0])}
        stock = read_rows(state / (job["deps"][0] + ".csv"))
        write_rows(destination, ["sku", "units", "cents"],
                   [{"sku": row["sku"], "units": row["units"], "cents": catalog[row["sku"]]}
                    for row in stock])
    elif job["kind"] == "quotes":
        prices = {row["sku"]: row for row in read_rows(state / (job["deps"][0] + ".csv"))}
        orders = read_rows(root / job["inputs"][0])
        rows = []
        for order in orders:
            price = prices[order["sku"]]
            units = min(int(order["requested"]), int(price["units"]))
            rows.append({"order": order["order"], "sku": order["sku"],
                         "units": units, "total_cents": units * int(price["cents"])})
        write_rows(destination, ["order", "sku", "units", "total_cents"], rows)
    elif job["kind"] == "settlements":
        rows = read_rows(root / job["inputs"][0])
        write_rows(destination, ["vendor", "cents"], rows)
    else:
        raise ValueError("unsupported job kind: " + job["kind"])
