# This module works, but it is messy on purpose. See EXERCISES.md.


def build_report(inventory):
    lines = []
    lines.append("INVENTORY REPORT")
    lines.append("================")
    cats = []
    for i in inventory.items.values():
        if i.category not in cats:
            cats.append(i.category)
    cats.sort()
    for c in cats:
        lines.append("")
        lines.append("[" + c + "]")
        t = 0
        for i in sorted(inventory.items.values(), key=lambda x: x.name):
            if i.category == c:
                v = i.quantity * i.price
                t = t + v
                lines.append("  " + i.name + " (" + i.sku + "): " + str(i.quantity) + " x $" + "%.2f" % i.price + " = $" + "%.2f" % v)
        lines.append("  subtotal: $" + "%.2f" % t)
    lines.append("")
    tt = 0
    for i in inventory.items.values():
        tt = tt + i.quantity * i.price
    lines.append("TOTAL: $" + "%.2f" % tt)
    return "\n".join(lines)
