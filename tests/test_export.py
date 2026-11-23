import csv
import io
import unittest

from inventory.export import write_csv
from inventory.models import Item
from inventory.store import Inventory


def export(*items):
    inv = Inventory()
    for item in items:
        inv.add_item(item)
    out = io.StringIO()
    write_csv(inv, out)
    return out.getvalue()


def rows(text):
    return list(csv.DictReader(io.StringIO(text)))


class TestWriteCsv(unittest.TestCase):
    def test_header_matches_item_fields(self):
        self.assertEqual(export().splitlines(), ["sku,name,quantity,price,category"])

    def test_rows_sorted_by_sku(self):
        text = export(Item("B2", "Bolt", 3, 0.1), Item("A1", "Axe", 1, 20.0, "tools"))
        self.assertEqual(
            text.splitlines()[1:],
            ["A1,Axe,1,20.0,tools", "B2,Bolt,3,0.1,general"],
        )

    def test_tricky_names_round_trip(self):
        names = [
            'Stephen "Chef" Curry, #30',
            "Luka Dončić — 🏆",
            '=HYPERLINK("http://example.com","MJ")',
        ]
        items = [Item(f"S{n}", name, 1, 1.0) for n, name in enumerate(names)]
        self.assertEqual([r["name"] for r in rows(export(*items))], names)

    def test_values_round_trip(self):
        [row] = rows(export(Item("P1", "Odd", 1000000, 19.99, "promo")))
        self.assertEqual(row, {"sku": "P1", "name": "Odd", "quantity": "1000000",
                               "price": "19.99", "category": "promo"})


if __name__ == "__main__":
    unittest.main()
