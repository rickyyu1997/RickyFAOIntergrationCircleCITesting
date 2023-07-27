from dataclasses import dataclass
from typing import Union, List
from decimal import Decimal


@dataclass(frozen=True)
class OrderItemsCancelledItem:
    id: str
    product_id: str


@dataclass(frozen=True)
class OrderItemsCancelledPayload:
    id: str
    items: List[OrderItemsCancelledItem]


@dataclass(frozen=True)
class OrderItemsCancelled:
    tenant: str
    name: str
    published_at: str
    payload: OrderItemsCancelledPayload
