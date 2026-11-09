from decimal import Decimal
from .money import money_text

def compact_export(rows, month):
    """Old compatibility summary retained for a spreadsheet plug-in."""
    subtotal = Decimal("0.00")
    count = 0
    for row in rows:
        if row["date"].strftime("%Y-%m") == month:
            subtotal += row["amount"]
            count += 1
    return {"month": month, "count": count, "total": money_text(subtotal)}
