from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, TypeVar, Generic, List

from newstore_common.newstore.event_stream.payment_refunded import PaymentTransaction, PaymentInstrument

T = TypeVar('T')


@dataclass(frozen=True)
class BaseEvent(Generic[T]):
    tenant: str
    name: str
    published_at: str
    payload: T


@dataclass(frozen=True)
class RefundRequestIssuedPayload:
    id: str
    order_id: str
    payment_account_id: str
    amount: Decimal
    currency: str
    requested_at: Optional[str]
    return_reason: Optional[str]
    reason_code: Optional[int]
    associate_id: Optional[str]
    associate_email: Optional[str]
    note: Optional[str]


@dataclass(frozen=True)
class RefundRequestIssued(BaseEvent[RefundRequestIssuedPayload]):
    payload: RefundRequestIssuedPayload


@dataclass(frozen=True)
class RefundRequestIssuedFinalPayload:
    refund_event: RefundRequestIssuedPayload
    transactions: List[PaymentTransaction]
    instruments: List[PaymentInstrument]


@dataclass(frozen=True)
class RefundRequestIssuedFinal(BaseEvent[RefundRequestIssuedFinalPayload]):
    payload: RefundRequestIssuedFinalPayload
