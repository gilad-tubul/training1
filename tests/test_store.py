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


class TestTrickyInputs(unittest.TestCase):
    def assertRejected(self, **overrides):
        fields = dict(sku="A1", name="Blue Widget", quantity=1, price=2.50, category="widgets")
        fields.update(overrides)
        with self.assertRaises(ValueError):
            Item(**fields)

    # 1. control characters (e.g. line breaks)
    def test_rejects_line_breaks_and_control_characters(self):
        for bad in ("Line1\nLine2", "Tab\there", "Bell\a"):
            with self.subTest(text=bad):
                self.assertRejected(name=bad)
                self.assertRejected(category=bad)
                self.assertRejected(sku=bad)

    # 2. surrounding whitespace
    def test_trims_surrounding_whitespace(self):
        item = Item("  A1 ", "  Blue Widget  ", 1, 2.50, "  widgets ")
        self.assertEqual((item.sku, item.name, item.category), ("A1", "Blue Widget", "widgets"))

    # 3. category case
    def test_category_is_lowercased(self):
        self.assertEqual(Item("A1", "Blue Widget", 1, 2.50, "Lakers").category, "lakers")

    # 4. empty values
    def test_rejects_empty_or_blank_text(self):
        for field in ("sku", "name", "category"):
            for bad in ("", "   "):
                with self.subTest(field=field, value=bad):
                    self.assertRejected(**{field: bad})

    # 5. same SKU, different category
    def test_add_same_sku_different_category_raises(self):
        inv = sample()
        with self.assertRaises(ValueError):
            inv.add_item(Item("A1", "Blue Widget", 1, 2.50, "heat"))
        self.assertEqual(inv.items["A1"].quantity, 10)

    def test_add_same_sku_category_differs_only_in_case_merges(self):
        inv = sample()
        inv.add_item(Item("A1", "Blue Widget", 1, 2.50, "WIDGETS"))
        self.assertEqual(inv.items["A1"].quantity, 11)

    # 6. accent-insensitive search
    def test_search_ignores_accents(self):
        inv = Inventory()
        inv.add_item(Item("L1", "Luka Dončić #77", 1, 34.99))
        inv.add_item(Item("L2", "Luka Doncic #77", 1, 34.99))
        for query in ("doncic", "DONČIĆ", "Dončić"):
            with self.subTest(query=query):
                self.assertEqual(sorted(i.sku for i in inv.search(query)), ["L1", "L2"])

    def test_search_casefolds(self):
        inv = Inventory()
        inv.add_item(Item("S1", "Straße Tee", 1, 10.0))
        self.assertEqual([i.sku for i in inv.search("STRASSE")], ["S1"])

    # 7. sub-cent prices
    def test_rejects_prices_with_more_than_two_decimals(self):
        self.assertRejected(price=19.999)
        self.assertRejected(price=0.001)

    def test_accepts_whole_cent_prices(self):
        for ok in (0, 0.1, 0.01, 34.99, 1234.56, 0.29):
            with self.subTest(price=ok):
                self.assertEqual(Item("A1", "Blue Widget", 1, ok).price, ok)

    # 8. whitespace inside a SKU
    def test_rejects_spaces_in_sku(self):
        self.assertRejected(sku="NBA LBJ 6")

    def test_names_may_contain_inner_spaces_and_symbols(self):
        name = 'Stephen "Chef" Curry, #30 — 🏆'
        self.assertEqual(Item("A1", name, 1, 1.0).name, name)


if __name__ == "__main__":
    unittest.main()
