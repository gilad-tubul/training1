import math
import unicodedata
from dataclasses import dataclass, asdict


@dataclass
class Item:
    sku: str
    name: str
    quantity: int
    price: float  # price per unit
    category: str = "general"

    def __post_init__(self):
        self.sku = _clean_text("SKU", self.sku)
        self.name = _clean_text("Name", self.name)
        self.category = _clean_text("Category", self.category).lower()
        if any(ch.isspace() for ch in self.sku):
            raise ValueError(f"SKU cannot contain spaces: {self.sku!r}")
        if self.quantity < 0:
            raise ValueError(f"Quantity cannot be negative: {self.quantity}")
        if not math.isfinite(self.price) or self.price < 0:
            raise ValueError(f"Price must be a non-negative number: {self.price}")
        if round(self.price, 2) != self.price:
            raise ValueError(f"Price cannot include fractions of a cent: {self.price}")

    @property
    def value(self):
        """Total value of this stock line: quantity times unit price."""
        return self.quantity * self.price

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


def _clean_text(label, text):
    """Trim surrounding whitespace; reject empty text and control characters."""
    text = text.strip()
    if not text:
        raise ValueError(f"{label} cannot be empty")
    if any(unicodedata.category(ch) == "Cc" for ch in text):
        raise ValueError(f"{label} cannot contain line breaks or control characters: {text!r}")
    return text
