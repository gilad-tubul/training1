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


class TestValidation(unittest.TestCase):
    # Bug 1: negative quantity on add
    def test_item_rejects_negative_quantity(self):
        with self.assertRaises(ValueError):
            Item("N1", "Negative", -3, 1.00)

    def test_add_negative_quantity_leaves_inventory_unchanged(self):
        inv = sample()
        with self.assertRaises(ValueError):
            inv.add_item(Item("A1", "Blue Widget", -3, 2.50, "widgets"))
        self.assertEqual(inv.items["A1"].quantity, 10)

    # Bug 2: negative quantity on remove
    def test_remove_negative_quantity_raises(self):
        inv = sample()
        with self.assertRaises(ValueError):
            inv.remove_item("A1", -10)
        self.assertEqual(inv.items["A1"].quantity, 10)

    # Bug 3: negative price
    def test_item_rejects_negative_price(self):
        with self.assertRaises(ValueError):
            Item("P1", "Cheap", 1, -9.00)

    def test_zero_price_is_allowed(self):
        self.assertEqual(Item("F1", "Freebie", 1, 0.0).price, 0.0)

    # Bug 4: same SKU with different details
    def test_add_same_sku_different_name_raises(self):
        inv = sample()
        with self.assertRaises(ValueError):
            inv.add_item(Item("A1", "Gadget", 1, 2.50, "widgets"))
        self.assertEqual(inv.items["A1"].name, "Blue Widget")
        self.assertEqual(inv.items["A1"].quantity, 10)

    def test_add_same_sku_different_price_raises(self):
        inv = sample()
        with self.assertRaises(ValueError):
            inv.add_item(Item("A1", "Blue Widget", 1, 99.00, "widgets"))
        self.assertEqual(inv.items["A1"].price, 2.50)
        self.assertEqual(inv.items["A1"].quantity, 10)

    def test_item_rejects_nan_and_infinite_price(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(price=bad), self.assertRaises(ValueError):
                Item("X1", "Bad", 1, bad)

if __name__ == "__main__":
    unittest.main()
