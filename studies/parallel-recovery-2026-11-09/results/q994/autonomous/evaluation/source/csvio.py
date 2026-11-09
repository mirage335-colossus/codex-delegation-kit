import csv
from datetime import date
from .money import parse_money

REQUIRED = ("date", "team", "status", "amount")

def read_expenses(path, warn=lambda message: None):
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or any(key not in reader.fieldnames for key in REQUIRED):
            raise ValueError("CSV must contain date, team, status, amount columns")
        for line, raw in enumerate(reader, start=2):
            try:
                day = date.fromisoformat(raw["date"].strip())
                team = raw["team"].strip()
                status = raw["status"].strip().lower()
                amount = parse_money(raw["amount"])
                if not team or amount < 0:
                    raise ValueError("team must be present and amount nonnegative")
            except (ValueError, AttributeError) as error:
                warn(f"line {line}: {error}")
                continue
            rows.append({"date": day, "team": team, "status": status, "amount": amount})
    return rows
