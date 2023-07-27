from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class FulfillmentRequestItemsReadyForHandoverItem:
    id: str
    product_id: str


@dataclass(frozen=True)
class FulfillmentRequestItemsReadyForHandoverPayload:
    id: str
    order_id: str
    logical_timestamp: int
    fulfillment_location_id: str
    service_level: str
    associate_id: Optional[str]
    items: List[FulfillmentRequestItemsReadyForHandoverItem]


@dataclass(frozen=True)
class FulfillmentRequestItemsReadyForHandover:
    tenant: str
    name: str
    published_at: str
    payload: FulfillmentRequestItemsReadyForHandoverPayload

