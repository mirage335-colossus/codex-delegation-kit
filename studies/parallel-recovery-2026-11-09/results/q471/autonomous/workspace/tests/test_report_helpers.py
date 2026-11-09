import unittest
from datetime import date
from decimal import Decimal
from source.aggregates import grand_total, totals_by_team
from source.rules import month_bounds, selected_expenses

class ReportHelperTests(unittest.TestCase):
    def row(self, day, team="East", status="approved", amount="2.50"):
        return {"date": date.fromisoformat(day), "team": team, "status": status,
                "amount": Decimal(amount)}

    def test_month_bounds_include_december_rollover(self):
        self.assertEqual(month_bounds("2026-12"), (date(2026, 12, 1), date(2027, 1, 1)))

    def test_selection_checks_status_and_both_month_edges(self):
        rows = [self.row("2026-10-01"), self.row("2026-10-31"),
                self.row("2026-11-01"), self.row("2026-10-04", status="rejected")]
        self.assertEqual(len(selected_expenses(rows, "2026-10")), 2)

    def test_aggregation_keeps_team_counts_and_decimal_totals(self):
        rows = [self.row("2026-10-01", "East", amount="1.20"),
                self.row("2026-10-02", "West", amount="3.00"),
                self.row("2026-10-03", "East", amount="0.80")]
        self.assertEqual(totals_by_team(rows)["East"], {"count": 2, "total": Decimal("2.00")})
        self.assertEqual(grand_total(rows), Decimal("5.00"))

if __name__ == "__main__":
    unittest.main()
