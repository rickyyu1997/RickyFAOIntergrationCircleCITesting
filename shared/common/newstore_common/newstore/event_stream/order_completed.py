from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class OrderCompletedItem:
    id: str
    product_id: str
    quantity: int
    status: str
    fulfillment_location_id: Optional[str]
    shipping_service_level: Optional[str]


@dataclass(frozen=True)
class OrderCompletedPayload:
    id: str
    items: List[OrderCompletedItem]


@dataclass(frozen=True)
class OrderCompleted:
    tenant: str
    name: str
    published_at: str
    payload: OrderCompletedPayload
