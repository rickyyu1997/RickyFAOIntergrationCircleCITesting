from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class FulfillmentRequestItemsCompletedItem:
    id: str
    product_id: str


@dataclass(frozen=True)
class FulfillmentRequestItemsCompletedPayload:
    id: str
    order_id: str
    logical_timestamp: int
    fulfillment_location_id: str
    associate_id: Optional[str]
    service_level: str
    items: List[FulfillmentRequestItemsCompletedItem]


@dataclass(frozen=True)
class FulfillmentRequestItemsCompleted:
    tenant: str
    name: str
    published_at: str
    payload: FulfillmentRequestItemsCompletedPayload

