from decimal import Decimal
from typing import List

from newstore_common.sfcc.xml_api.order.common_fields import ValuedObject
from newstore_common.sfcc.xml_api.order.line_item import ProductLineItem
from newstore_common.sfcc.xml_api.order.order_data import Order
from newstore_common.sfcc.order_injector.tools import get_price


class DiscountCalculator:

    def __init__(
            self,
            order: Order
    ):
        self.is_tax_included = order.is_tax_included
        self.total_order_discount = self.calculate_total_order_discount_amount(order)
        self.total_items_with_item_discount = self.calculate_merchandize_total_with_discount(
            order.product_lineitems)

    def calculate_merchandize_total_with_discount(self, items: List[ProductLineItem]) -> Decimal:
        return sum(map(lambda item: self.calculate_item_price_with_discount(item), items))

    def calculate_total_order_discount_amount(self, order: Order) -> Decimal:
        if order.totals.merchandize_total.price_adjustments is None:
            return Decimal(0)
        else:
            order_discounts = order.totals.merchandize_total.price_adjustments
            return sum(map(lambda discount: self.get_price_value(discount), order_discounts))

    def calculate_order_discount(self, item: ProductLineItem) -> Decimal:
        item_with_item_discount = self.calculate_item_price_with_discount(item)
        proportion_of_total = item_with_item_discount / self.total_items_with_item_discount
        return round(abs(self.total_order_discount * proportion_of_total), 2)

    def calculate_item_price_with_discount(self, item: ProductLineItem):
        if item.price_adjustments:
            total_item_discount = abs(sum(self.get_price_value(discount)
                                          for discount in item.price_adjustments))
        else:
            total_item_discount = 0
        return self.get_price_value(item) - total_item_discount

    def get_price_value(self, priced_object: ValuedObject) -> Decimal:
        return abs(get_price(priced_object, self.is_tax_included))
