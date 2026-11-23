import io
import unittest

from inventory.export import write_csv
from inventory.importer import read_csv
from inventory.models import Item
from inventory.store import Inventory


def read(text):
    return read_csv(io.StringIO(text))


class TestReadCsv(unittest.TestCase):
    def assertFails(self, text, *fragments):
        with self.assertRaises(ValueError) as ctx:
            read(text)
        for fragment in fragments:
            self.assertIn(fragment, str(ctx.exception))

    def test_reads_rows_with_line_numbers(self):
        rows = read("sku,name,quantity,price,category\nA1,Axe,2,20.0,tools\nB1,Bolt,3,0.1,hardware\n")
        self.assertEqual(
            [(line, item.sku, item.quantity, item.price, item.category) for line, item in rows],
            [(2, "A1", 2, 20.0, "tools"), (3, "B1", 3, 0.1, "hardware")],
        )

    def test_round_trips_export_output(self):
        inv = Inventory()
        for item in [Item("Q1", 'Stephen "Chef" Curry, #30', 5, 34.99, "warriors"),
                     Item("U1", "Luka Dončić — 🏆", 1, 0, "lakers"),
                     Item("F1", '=HYPERLINK("http://x","MJ")', 1000000, 0.01, "legends")]:
            inv.add_item(item)
        out = io.StringIO()
        write_csv(inv, out)
        self.assertEqual([item for _, item in read(out.getvalue())],
                         [inv.items[sku] for sku in sorted(inv.items)])

    def test_columns_in_any_order_and_category_optional(self):
        [(_, item)] = read("price,quantity,name,sku\n2.5,4,Widget,W1\n")
        self.assertEqual((item.sku, item.name, item.quantity, item.price, item.category),
                         ("W1", "Widget", 4, 2.5, "general"))

    def test_empty_category_cell_defaults_to_general(self):
        [(_, item)] = read("sku,name,quantity,price,category\nW1,Widget,4,2.5,\n")
        self.assertEqual(item.category, "general")

    def test_missing_category_uses_default_category_callback(self):
        rows = read_csv(io.StringIO("sku,name,quantity,price\n A1 ,Axe,1,20\n"),
                        default_category=lambda sku: f"for-{sku}")
        self.assertEqual(rows[0][1].category, "for-a1")

    def test_excel_byte_order_mark_is_ignored(self):
        [(_, item)] = read("﻿sku,name,quantity,price\nW1,Widget,4,2.5\n")
        self.assertEqual(item.sku, "W1")

    def test_blank_lines_are_skipped(self):
        self.assertEqual(len(read("sku,name,quantity,price\n\nW1,Widget,4,2.5\n\n")), 1)

    def test_header_only_gives_no_rows(self):
        self.assertEqual(read("sku,name,quantity,price\n"), [])

    def test_empty_file_fails(self):
        self.assertFails("", "empty")

    def test_missing_required_column_fails(self):
        self.assertFails("sku,name,price\nW1,Widget,2.5\n", "missing", "quantity")

    def test_unknown_column_fails(self):
        self.assertFails("sku,name,qty,price\nW1,Widget,4,2.5\n", "unknown", "qty")

    def test_bad_quantity_names_the_line(self):
        self.assertFails("sku,name,quantity,price\nW1,Widget,4,2.5\nW2,Gadget,2.5,1\n",
                         "line 3", "quantity", "2.5")

    def test_bad_price_names_the_line(self):
        self.assertFails("sku,name,quantity,price\nW1,Widget,4,$2.50\n", "line 2", "price", "$2.50")

    def test_item_validation_errors_name_the_line(self):
        self.assertFails("sku,name,quantity,price\nW1,,4,2.5\n", "line 2", "Name cannot be empty")

    def test_missing_cell_fails(self):
        self.assertFails("sku,name,quantity,price\nW1,Widget,4\n", "line 2", "price")

    def test_extra_cell_fails(self):
        self.assertFails("sku,name,quantity,price\nW1,Widget,4,2.5,oops\n", "line 2", "more values")

    def test_duplicate_sku_fails(self):
        self.assertFails("sku,name,quantity,price\nW1,Widget,4,2.5\nB1,Bolt,1,1\n W1 ,Widget,1,2.5\n",
                         "line 4", "W1", "line 2")


if __name__ == "__main__":
    unittest.main()
