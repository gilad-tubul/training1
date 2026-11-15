import json
from pathlib import Path

from .models import Item


class Inventory:
    """Holds items in memory and can save/load them to a JSON file."""

    def __init__(self):
        self.items = {}

    def add_item(self, item):
        if item.sku in self.items:
            self.items[item.sku].quantity += item.quantity
        else:
            self.items[item.sku] = item

    def remove_item(self, sku, quantity):
        if sku not in self.items:
            raise KeyError(f"Unknown SKU: {sku}")
        item = self.items[sku]
        item.quantity -= quantity
        if item.quantity == 0:
            del self.items[sku]

    def total_value(self):
        return sum(i.quantity * i.price for i in self.items.values())

    def low_stock(self, threshold=5):
        """Return items whose quantity is at or below the threshold."""
        return [i for i in self.items.values() if i.quantity < threshold]

    def search(self, text):
        """Find items whose name contains text, ignoring case."""
        return [i for i in self.items.values() if text in i.name]

    def save(self, path):
        data = [i.to_dict() for i in self.items.values()]
        Path(path).write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path):
        inv = cls()
        for row in json.loads(Path(path).read_text()):
            inv.add_item(Item.from_dict(row))
        return inv
