from collections import defaultdict
from decimal import Decimal


def totals_by_team(rows):
    """Accumulate count and exact Decimal total for each team."""
    result = defaultdict(lambda: {"count": 0, "total": Decimal("0.00")})
    for row in rows:
        slot = result[row["team"]]
        slot["count"] += 1
        slot["total"] += row["amount"]
    return dict(result)


def grand_total(rows):
    total = Decimal("0.00")
    for row in rows:
        total += row["amount"]
    return total
