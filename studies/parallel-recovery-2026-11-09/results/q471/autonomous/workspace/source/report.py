from .aggregates import grand_total, totals_by_team
from .money import money_text
from .rules import selected_expenses

def build_monthly_report(rows, month):
    """Build a finance report from already validated expense rows."""
    selected = selected_expenses(rows, month)
    by_team = totals_by_team(selected)
    return {
        "month": month,
        "grand_total": money_text(grand_total(selected)),
        "teams": {name: {"count": item["count"], "total": money_text(item["total"])}
                  for name, item in sorted(by_team.items())},
    }
