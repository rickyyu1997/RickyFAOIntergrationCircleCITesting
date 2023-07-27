from dataclasses import dataclass
from typing import Union, List, Optional
from decimal import Decimal


@dataclass(frozen=True)
class PaymentTransaction:
    id: str
    instrument_id: str
    amount: Decimal
    currency: str
    correlation_id: str


@dataclass(frozen=True)
class PaymentInstrument:
    id: str
    payment_method: str
    payment_wallet: str
    payment_provider: str


@dataclass(frozen=True)
class PaymentAccountAmountRefundedPayload:
    id: str
    order_id: str
    transactions: List[PaymentTransaction]
    instruments: List[PaymentInstrument]


@dataclass(frozen=True)
class PaymentAccountAmountRefunded:
    tenant: str
    name: str
    published_at: str
    payload: PaymentAccountAmountRefundedPayload
