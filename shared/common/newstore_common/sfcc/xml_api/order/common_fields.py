from decimal import Decimal
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class TextNode:
    attributes: Dict
    text: str


@dataclass(frozen=True)
class ValuedObject:
    gross_price: Decimal
    net_price: Decimal
