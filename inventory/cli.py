import argparse
import sys
from pathlib import Path

from .models import Item
from .report import build_report
from .store import Inventory

DEFAULT_FILE = "inventory.json"


def _load(path):
    if not Path(path).exists():
        return Inventory()
    try:
        return Inventory.load(path)
    except (KeyError, TypeError, ValueError) as e:
        # Bad JSON, unknown/missing fields, or values that fail Item validation.
        raise ValueError(f"Could not load {path}: {e}") from e


def main(argv=None):
    parser = argparse.ArgumentParser(prog="inventory")
    parser.add_argument("--file", default=DEFAULT_FILE)
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add stock")
    add.add_argument("sku")
    add.add_argument("name")
    add.add_argument("quantity", type=int)
    add.add_argument("price", type=float)
    add.add_argument("--category", default="general")

    remove = sub.add_parser("remove", help="remove stock")
    remove.add_argument("sku")
    remove.add_argument("quantity", type=int)

    sub.add_parser("list", help="list all items")
    sub.add_parser("report", help="print a report grouped by category")

    args = parser.parse_args(argv)
    try:
        _run(args)
    except (KeyError, ValueError) as e:
        # Use args[0]: str() of a KeyError wraps the message in quotes.
        print(f"error: {e.args[0]}", file=sys.stderr)
        return 1
    return 0


def _run(args):
    inv = _load(args.file)

    if args.command == "add":
        inv.add_item(Item(args.sku, args.name, args.quantity, args.price, args.category))
        inv.save(args.file)
    elif args.command == "remove":
        inv.remove_item(args.sku, args.quantity)
        inv.save(args.file)
    elif args.command == "list":
        for item in inv.items.values():
            print(f"{item.sku}\t{item.name}\t{item.quantity}\t${item.price:.2f}")
    elif args.command == "report":
        print(build_report(inv))


if __name__ == "__main__":
    sys.exit(main())
