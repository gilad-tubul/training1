from dataclasses import dataclass, asdict


@dataclass
class Item:
    sku: str
    name: str
    quantity: int
    price: float  # price per unit
    category: str = "general"

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
