import unittest

from inventory.models import Item
from inventory.report import build_report
from inventory.store import Inventory

EXPECTED = """INVENTORY REPORT
================

[hardware]
  Steel Bolt (B1): 100 x $0.10 = $10.00
  subtotal: $10.00

[widgets]
  Blue Widget (A1): 10 x $2.50 = $25.00
  Red Widget (A2): 5 x $3.00 = $15.00
  subtotal: $40.00

TOTAL: $50.00"""


class TestReport(unittest.TestCase):
    def test_report_output_is_stable(self):
        inv = Inventory()
        inv.add_item(Item("A2", "Red Widget", 5, 3.00, "widgets"))
        inv.add_item(Item("B1", "Steel Bolt", 100, 0.10, "hardware"))
        inv.add_item(Item("A1", "Blue Widget", 10, 2.50, "widgets"))
        self.assertEqual(build_report(inv), EXPECTED)


if __name__ == "__main__":
    unittest.main()
