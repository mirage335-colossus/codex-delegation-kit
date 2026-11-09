import unittest
from decimal import Decimal
from source.money import parse_money, money_text

class MoneyTests(unittest.TestCase):
    def test_currency_and_grouping(self):
        self.assertEqual(parse_money("$1,240.125"), Decimal("1240.13"))

    def test_text(self):
        self.assertEqual(money_text(Decimal("3")), "3.00")

if __name__ == "__main__":
    unittest.main()
