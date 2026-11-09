from datetime import date


def month_bounds(month):
    """Return inclusive start and exclusive end dates for a calendar month."""
    if not isinstance(month, str) or len(month) != 7 or month[4] != "-":
        raise ValueError("month must be YYYY-MM")
    try:
        year, number = (int(part) for part in month.split("-"))
        start = date(year, number, 1)
    except (TypeError, ValueError) as error:
        raise ValueError("month must be a real calendar month") from error
    if start.strftime("%Y-%m") != month:
        raise ValueError("month must be YYYY-MM")
    if number == 12:
        stop = date(year + 1, 1, 1)
    else:
        stop = date(year, number + 1, 1)
    return start, stop


def selected_expenses(rows, month):
    """Select approved rows that belong to the requested calendar month."""
    start, stop = month_bounds(month)
    return [row for row in rows
            if row["status"] == "approved" and start <= row["date"] < stop]
