import logging
import json
import traceback
from dataclasses import asdict, dataclass
from enum import IntEnum
from typing import Dict, Any, Optional
from newstore_adapter.connector import NewStoreConnector
from newstore_common.json.decimal_encoder import DecimalToStringEncoder, DecimalToValueEncoder
from newstore_common.sfcc.xml_api.order.order_data import Payment, Order
from newstore_common.sfcc.xml_api.order.address import Address
from newstore_common.newstore.api.fulfill_order import NewStoreOrder, NewStoreShipment, NewStoreAddress, NewStorePayment
from newstore_common.sfcc.order_injector.discount_calculator import DiscountCalculator
from newstore_common.sfcc.order_injector.item_builder import LineItemBuilder
from newstore_common.sfcc.order_injector.payment_builder import PaymentBuilder
from newstore_common.sfcc.order_injector.shipment_builder import ShipmentBuilder
from newstore_common.sfcc.order_injector.tax_calculator import TaxCalculator
import newstore_common.sfcc.order_injector.tools as order_injector_tools
from newstore_common.sfcc.order_injector.shipping_config_builder import ShippingConfigBuilder
from newstore_common.error.error import Error

logger = logging.getLogger(__name__)


class ErrorReason(IntEnum):
    UNEXPECTED = 0
    TRANSFORM_UNEXPECTED = 100
    INJECT_UNEXPECTED = 200
    INJECT_SAME_ORDER_WITH_DIFFERENT_DATA = 201


@dataclass(frozen=True)
class InjectorError(Error):
    reason: ErrorReason
    message: str
    stacktrace: Optional[str]

    @property
    def error(self) -> str:
        return f"Error: {self.reason.name}[{self.reason}] => {self.message}\n\n{self.stacktrace}"


class OrderInjector:

    def __init__(self, connector: NewStoreConnector, payment_builder: PaymentBuilder, shipping_config_builder: ShippingConfigBuilder):
        self.connector = connector
        self._payment_builder = payment_builder
        self.shipping_config_builder = shipping_config_builder

    def process(self, order: Order) -> (NewStoreOrder, Optional[InjectorError]):
        logger.info(f'Building order from: {json.dumps(asdict(order), cls=DecimalToStringEncoder)}')

        try:
            newstore_order = self._build_order(order)
            payload = self._format_payload(newstore_order)
        except Exception as ex:
            error = InjectorError(reason=ErrorReason.TRANSFORM_UNEXPECTED, message=f"[{type(ex).__name__}] {str(ex)}", stacktrace=traceback.format_stack())
            return None, error

        try:
            response = self.connector.fulfill_order(payload)

            if response:
                result = json.dumps(response, indent=4)
            else:
                result = response.text
            logger.info(f'Received response: {result}')

            return response, None

        except Exception as ex:
            reason = ErrorReason.INJECT_UNEXPECTED
            if "same_order_injection_with_different_data" in str(ex):
                reason = ErrorReason.INJECT_SAME_ORDER_WITH_DIFFERENT_DATA
            error = InjectorError(reason=reason, message=str(ex), stacktrace=traceback.format_exc(ex))
            return None, error

    @staticmethod
    def tax_is_included_in_prices(order: Order):
        return order.taxation != 'net'

    def _format_payload(self, newstore_order: NewStoreOrder) -> Dict:
        payload = json.loads(json.dumps(asdict(newstore_order), cls=DecimalToValueEncoder))
        logger.info(f'Sending payload: {json.dumps(payload, indent=4)}')
        self._remove_null_values(payload)
        return payload

    def _build_order(self, order: Order) -> NewStoreOrder:
        return NewStoreOrder(
            external_id=order.order_id,
            placed_at=order.order_date,
            shop='storefront-catalog-en',
            channel_type='web',
            channel_name='SFCC',
            currency=order.currency,
            external_customer_id=order.customer.customer_no,
            customer_name=order.customer.customer_name,
            customer_email=order.customer.customer_email,
            shop_locale='en-US',
            customer_language=order.customer_language,
            price_method=order.price_method,
            billing_address=self._build_address(order.billing_address),
            shipping_address=self._build_address(order.billing_address),
            is_preconfirmed=False,
            is_historical=False,
            payments=[self._build_payments(payment=payment, order=order)
                      for payment in order.payments],
            shipments=[self._build_combined_shipment(order)]
        )

    def _build_combined_shipment(self, order: Order) -> NewStoreShipment:
        shipment_builder = self._create_shipment_builder(order)
        line_item_builder = self._create_line_item_builder(order)
        shipment = order.shipments[0]
        return shipment_builder.build_shipment(
            shipment=shipment,
            line_items=line_item_builder.build_items(
                order.product_lineitems,
                order.combined_merchandize_discount),
            shipping_discounts=[
                order_injector_tools.format_discount(discount, order.is_tax_included)
                for line_item in order.shipping_lineitems
                if line_item.price_adjustments
                for discount in line_item.price_adjustments])

    def _build_payments(self, payment: Payment, order: Order) -> NewStorePayment:
        return self._payment_builder.build(
            payment,
            order.order_date,
            order.custom_attributes)

    @staticmethod
    def _build_address(address: Address) -> NewStoreAddress:
        return NewStoreAddress(
            first_name=address.first_name,
            last_name=address.last_name,
            country=address.country_code,
            zip_code=address.postal_code,
            city=address.city,
            state=address.state,
            phone=address.phone,
            address_line_1=address.address1,
            address_line_2=address.address2)

    def _create_line_item_builder(self, order: Order) -> LineItemBuilder:
        tax_is_included = self.tax_is_included_in_prices(order)
        tax_calculator = TaxCalculator(tax_is_included=tax_is_included)
        return LineItemBuilder(
            tax_is_included=tax_is_included,
            tax_calculator=tax_calculator,
            discount_calculator=DiscountCalculator(order))

    def _create_shipment_builder(self, order: Order) -> ShipmentBuilder:
        return ShipmentBuilder(
            self.shipping_config_builder,
            is_tax_included=self.tax_is_included_in_prices(order),
            combined_merchandize_discount=order.combined_merchandize_discount)

    def _remove_null_values(self, payload: Any):
        if type(payload) == dict:
            keys = list(payload.keys())
            for key in keys:
                if payload[key] is None:
                    del payload[key]
                else:
                    self._remove_null_values(payload[key])
        elif type(payload) == list:
            for element in payload:
                self._remove_null_values(element)

