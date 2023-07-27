from dataclasses import dataclass, asdict
from decimal import Decimal
from typing import Dict, List
from newstore_common.newstore.api.fulfill_order import NewStorePayment
from newstore_common.sfcc.xml_api.order.common_fields import TextNode
from newstore_common.sfcc.xml_api.order.order_data import Payment


@dataclass(frozen=True)
class PaymentInfo:
    processor: str
    method: str
    correlation_ref: str


class PaymentInfoExtractor:

    def extract(self, payment: Payment, order_custom_attributes: List[TextNode]) -> PaymentInfo:
        raise NotImplementedError()


class PaymentBuilder:

    def __init__(self, formatting_methods: Dict[str, PaymentInfoExtractor]):
        self.formatting_methods = formatting_methods

    def build(
            self,
            payment: Payment,
            order_date: str,
            order_custom_attributes: List[TextNode]) -> NewStorePayment:
        payment_type = self.get_payment_type(payment)

        if payment_type in self.formatting_methods:
            formatting_method = self.formatting_methods[payment_type]
            return self._create_newstore_payment(
                info=formatting_method.extract(payment, order_custom_attributes),
                amount=payment.amount,
                order_date=order_date)
        else:
            raise Exception(f"Unknown payment type => {payment_type}")

    def get_payment_type(self, payment: Payment) -> str:
        raise NotImplementedError(f"[{self.__class__.__name__}] get_payment_type() must be implemented")

    @staticmethod
    def _create_newstore_payment(
            info: PaymentInfo,
            amount: Decimal,
            order_date: str) -> NewStorePayment:
        return NewStorePayment(
            method=info.method,
            processor=info.processor,
            correlation_ref=info.correlation_ref,
            amount=amount,
            processed_at=order_date,
            type='captured')
