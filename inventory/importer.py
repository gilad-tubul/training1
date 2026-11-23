"""Read items from other formats."""

import csv

from .export import CSV_COLUMNS
from .models import Item

REQUIRED_COLUMNS = [c for c in CSV_COLUMNS if c != "category"]
_EXTRA = object()  # DictReader key for cells beyond the header


def read_csv(file, default_category=lambda sku: "general"):
    """Parse CSV rows into Items, returning a list of (line number, Item) pairs.

    default_category(sku) supplies the category when the column is absent or the
    cell is blank.

    Raises ValueError with a message starting "header:" or "line N:" on the first
    problem, so callers can prefix it with the file name. Open files with
    newline="" and encoding="utf-8-sig" (the latter drops Excel's byte order mark).
    """
    reader = csv.DictReader(file, restkey=_EXTRA)
    if reader.fieldnames is None:
        raise ValueError("header: missing, the file is empty")
    reader.fieldnames = header = [h.lstrip("﻿").strip().lower() for h in reader.fieldnames]
    _check_header(header)

    rows, first_seen = [], {}
    for row in reader:
        line = reader.line_num
        try:
            item = _parse_row(row, header, default_category)
        except ValueError as e:
            raise ValueError(f"line {line}: {e}") from e
        if item.sku in first_seen:
            raise ValueError(
                f"line {line}: SKU {item.sku} already appears on line {first_seen[item.sku]}"
            )
        first_seen[item.sku] = line
        rows.append((line, item))
    return rows


def _check_header(header):
    duplicates = sorted({h for h in header if header.count(h) > 1})
    unknown = [h for h in header if h not in CSV_COLUMNS]
    missing = [c for c in REQUIRED_COLUMNS if c not in header]
    for problem, names in (("duplicate", duplicates), ("unknown", unknown), ("missing", missing)):
        if names:
            raise ValueError(
                f"header: {problem} column(s) {', '.join(map(repr, names))}; "
                f"expected {', '.join(CSV_COLUMNS)}"
            )


def _parse_row(row, header, default_category):
    if _EXTRA in row:
        raise ValueError(f"has more values than the {len(header)} columns")
    blank = [c for c in header if row[c] is None]
    if blank:
        raise ValueError(f"missing value for {blank[0]!r}")

    quantity = _convert(int, row["quantity"], "quantity", "a whole number")
    price = _convert(float, row["price"], "price", "a number like 34.99")
    category = (row.get("category") or "").strip() or default_category(row["sku"].strip())
    return Item(row["sku"], row["name"], quantity, price, category)


def _convert(kind, raw, column, expected):
    try:
        return kind(raw.strip())
    except ValueError:
        raise ValueError(f"{column} must be {expected}, got {raw!r}") from None
