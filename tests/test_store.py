import tempfile
import unittest
from pathlib import Path

from inventory.models import Item
from inventory.store import Inventory


def sample():
    inv = Inventory()
    inv.add_item(Item("A1", "Blue Widget", 10, 2.50, "widgets"))
    inv.add_item(Item("A2", "Red Widget", 5, 3.00, "widgets"))
    inv.add_item(Item("B1", "Steel Bolt", 100, 0.10, "hardware"))
    return inv


class TestInventory(unittest.TestCase):
    def test_add_merges_same_sku(self):
        inv = sample()
        inv.add_item(Item("A1", "Blue Widget", 3, 2.50, "widgets"))
        self.assertEqual(inv.items["A1"].quantity, 13)

    def test_total_value(self):
        self.assertAlmostEqual(sample().total_value(), 25 + 15 + 10)

    def test_remove_reduces_quantity(self):
        inv = sample()
        inv.remove_item("A1", 4)
        self.assertEqual(inv.items["A1"].quantity, 6)

    def test_remove_more_than_in_stock_raises(self):
        inv = sample()
        with self.assertRaises(ValueError):
            inv.remove_item("A2", 6)
        self.assertEqual(inv.items["A2"].quantity, 5)

    def test_low_stock_includes_threshold(self):
        names = [i.name for i in sample().low_stock(threshold=5)]
        self.assertEqual(names, ["Red Widget"])

    def test_search_is_case_insensitive(self):
        names = sorted(i.name for i in sample().search("widget"))
        self.assertEqual(names, ["Blue Widget", "Red Widget"])

    def test_save_and_load_round_trip(self):
        inv = sample()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "inv.json"
            inv.save(path)
            loaded = Inventory.load(path)
        self.assertEqual(loaded.items, inv.items)


if __name__ == "__main__":
    unittest.main()
