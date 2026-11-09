from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")

def parse_money(value):
    """Convert a CSV amount to an exact, two-place Decimal."""
    try:
        amount = Decimal(str(value).strip().replace("$", "").replace(",", ""))
    except (InvalidOperation, AttributeError):
        raise ValueError(f"invalid amount: {value!r}")
    if not amount.is_finite():
        raise ValueError(f"invalid amount: {value!r}")
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)

def money_text(amount):
    return f"{amount.quantize(CENT):.2f}"
