from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class ReturnProcessedItem:
    id: str
    product_id: str
    quantity: int
    refund_amount: Decimal
    refund_amount_adjusted: Decimal
    refund_excl_tax: Decimal
    refund_tax: Decimal
    item_condition: Optional[str]
    condition_code: Optional[int]
    return_reason: Optional[str]
    return_code: Optional[int]


@dataclass(frozen=True)
class ReturnProcessedPayload:
    id: str
    order_id: Optional[str]
    returned_at: str
    total_refund_amount: Decimal
    total_refund_amount_adjusted: Decimal
    total_refund_excl_tax: Decimal
    total_refund_tax: Decimal
    return_fee: Decimal
    currency: str
    return_location_id: str
    customer_id: Optional[str]
    customer_email: Optional[str]
    associate_id: Optional[str]
    associate_email: Optional[str]
    items: List[ReturnProcessedItem]


@dataclass(frozen=True)
class ReturnProcessed:
    tenant: str
    name: str
    published_at: str
    payload: ReturnProcessedPayload
