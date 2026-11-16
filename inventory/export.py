"""Export the inventory to other formats."""

import csv
from dataclasses import fields

from .models import Item

CSV_COLUMNS = [f.name for f in fields(Item)]


def write_csv(inventory, file):
    """Write one row per item, sorted by SKU, to an open text file.

    Open files with newline="" so the csv module controls line endings.
    """
    writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    for sku in sorted(inventory.items):
        writer.writerow(inventory.items[sku].to_dict())
