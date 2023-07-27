from decimal import Decimal
from typing import List
from newstore_common.newstore.api.fulfill_order import NewStoreShipment, NewStoreShippingOption, NewStoreItem, NewStoreDiscount
from newstore_common.sfcc.xml_api.order.common_fields import ValuedObject
from newstore_common.sfcc.xml_api.order.order_data import Shipment
from newstore_common.sfcc.xml_api.order.totals import PriceAdjustment
from newstore_common.sfcc.order_injector.shipping_config_builder import ShippingConfigBuilder
from newstore_common.sfcc.order_injector.tools import get_price


class ShipmentBuilder:

    def __init__(
            self,
            shipping_config_builder: ShippingConfigBuilder,
            combined_merchandize_discount: PriceAdjustment,
            is_tax_included: bool
    ):
        self.shipping_config_builder = shipping_config_builder
        self._is_tax_included = is_tax_included
        self._combined_merchandize_discount = combined_merchandize_discount

    def build_shipment(
            self,
            shipment: Shipment,
            line_items: List[NewStoreItem],
            shipping_discounts: List[NewStoreDiscount]) -> NewStoreShipment:
        shipping_option = self._build_shipping_option(
            shipment=shipment,
            shipping_discounts=shipping_discounts)
        return NewStoreShipment(
            items=line_items,
            shipping_option=shipping_option)

    def _build_shipping_option(
            self,
            shipment: Shipment,
            shipping_discounts: List[NewStoreDiscount]) -> NewStoreShippingOption:
        shipping_cost = self.get_price_value(shipment.totals.adjusted_shipping_total)
        shipping_tax = round(shipment.totals.adjusted_shipping_total.tax, 2)
        shipping_config = self.shipping_config_builder.get_shipping_config(shipment)
        return NewStoreShippingOption(
            service_level_identifier=shipping_config.service_level,
            shipping_type=shipping_config.shipping_type,
            carrier=shipping_config.shipping_carrier_name,
            display_name=shipment.shipping_method,
            fulfillment_node_id=shipping_config.fulfillment_node_id,
            zip_code=shipment.shipping_address.postal_code,
            country_code=shipment.shipping_address.country_code,
            price=shipping_cost,
            tax=shipping_tax,
            discount_info=shipping_discounts)

    def get_price_value(self, priced_obj: ValuedObject) -> Decimal:
        return get_price(priced_obj, self._is_tax_included)
