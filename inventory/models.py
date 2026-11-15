from dataclasses import dataclass, asdict


@dataclass
class Item:
    sku: str
    name: str
    quantity: int
    price: float  # price per unit
    category: str = "general"

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError(f"Quantity cannot be negative: {self.quantity}")
        if self.price < 0:
            raise ValueError(f"Price cannot be negative: {self.price}")

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
