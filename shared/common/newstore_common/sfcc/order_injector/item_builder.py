from decimal import Decimal
from typing import List, Optional
from newstore_common.sfcc.xml_api.order.common_fields import ValuedObject
from newstore_common.sfcc.xml_api.order.line_item import ProductLineItem
from newstore_common.sfcc.xml_api.order.totals import PriceAdjustment
from newstore_common.sfcc.order_injector.discount_calculator import DiscountCalculator
from newstore_common.sfcc.order_injector.tax_calculator import TaxCalculator
import newstore_common.sfcc.order_injector.tools as order_injector_tools
from newstore_common.newstore.api.fulfill_order import NewStoreItem, NewStoreItemPrice, NewStoreTaxLine


class LineItemBuilder:

    def __init__(
            self,
            tax_is_included: bool,
            tax_calculator: TaxCalculator,
            discount_calculator: DiscountCalculator
    ):
        self._is_tax_included = tax_is_included
        self.discount_calculator = discount_calculator
        self.tax_calculator = tax_calculator

    def build_items(
            self,
            items: List[ProductLineItem],
            combined_merchandize_discount: Optional[PriceAdjustment]
    ) -> List[NewStoreItem]:
        order_discount_remaining = self.discount_calculator.total_order_discount
        newstore_items = []
        for item in items[:-1]:
            order_discount_value = self.discount_calculator.calculate_order_discount(item)
            order_discount_remaining -= order_discount_value
            newstore_items.append(self._build_newstore_item(
                item=item,
                combined_merchandize_discount=combined_merchandize_discount,
                item_order_discount_value=order_discount_value))
        newstore_items.append(self._build_newstore_item(
            item=items[-1],
            combined_merchandize_discount=combined_merchandize_discount,
            item_order_discount_value=order_discount_remaining))
        return newstore_items

    def _build_newstore_item(self,
                             item: ProductLineItem,
                             combined_merchandize_discount: Optional[PriceAdjustment],
                             item_order_discount_value: Decimal) -> NewStoreItem:
        item_discounts = (
            [] if not item.price_adjustments else
            [order_injector_tools.format_discount(discount, self._is_tax_included)
             for discount in item.price_adjustments])
        order_discounts = (
            [] if not combined_merchandize_discount else
            [order_injector_tools.format_discount(
                combined_merchandize_discount,
                override_amount=item_order_discount_value,
                is_tax_included=self._is_tax_included)])
        item_price_with_item_discount = self.discount_calculator.calculate_item_price_with_discount(item)
        item_price = item_price_with_item_discount - item_order_discount_value
        tax_lines = [self._format_tax_line(item, item_price)]

        return NewStoreItem(
            external_item_id=item.product_id,
            product_id=item.product_id,
            price=NewStoreItemPrice(
                item_list_price=self._get_price_value(item),
                item_price=item_price,
                item_tax_lines=tax_lines),
            item_discount_info=item_discounts,
            item_order_discount_info=order_discounts)

    def _format_tax_line(self, item: ProductLineItem, item_price: Decimal) -> NewStoreTaxLine:
        return NewStoreTaxLine(amount=self.tax_calculator.get_tax_amount(item, item_price),
                               rate=self.tax_calculator.get_tax_rate(item, item_price))

    def _get_price_value(self, priced_object: ValuedObject) -> Decimal:
        return order_injector_tools.get_price(priced_object, self._is_tax_included)
