"""Plain-text inventory report, grouped by category."""

from collections import defaultdict


def build_report(inventory):
    """Return a report listing items by category, with subtotals and a total."""
    lines = ["INVENTORY REPORT", "================"]

    for category, items in sorted(_group_by_category(inventory).items()):
        lines += ["", f"[{category}]"]
        lines += [_item_line(item) for item in items]
        subtotal = sum(item.value for item in items)
        lines.append(f"  subtotal: {_money(subtotal)}")

    lines += ["", f"TOTAL: {_money(inventory.total_value())}"]
    return "\n".join(lines)


def _group_by_category(inventory):
    """Map each category to its items, sorted by name."""
    groups = defaultdict(list)
    for item in sorted(inventory.items.values(), key=lambda i: i.name):
        groups[item.category].append(item)
    return groups


def _item_line(item):
    return (
        f"  {item.name} ({item.sku}): "
        f"{item.quantity} x {_money(item.price)} = {_money(item.value)}"
    )


def _money(amount):
    return f"${amount:.2f}"
