from decimal import Decimal
from newstore_common.sfcc.xml_api.order.line_item import ProductLineItem


class TaxCalculator:

    def __init__(self, tax_is_included: bool):
        self.tax_is_included = tax_is_included

    def get_tax_rate(
            self,
            item: ProductLineItem,
            item_price: Decimal) -> Decimal:
        return (
            item.tax_rate
            if item.tax_rate else
            self._calculate_tax_rate(tax_amount=item.tax, item_price=item_price))

    def _calculate_tax_rate(self, item_price: Decimal, tax_amount: Decimal) -> Decimal:
        tax_rate = (
            tax_amount / (tax_amount + item_price)
            if self.tax_is_included else
            tax_amount / item_price)
        return round(tax_rate, 5)

    def get_tax_amount(self, item: ProductLineItem, item_price) -> Decimal:
        rate = self.get_tax_rate(item, item_price)
        return self._calculate_tax_amount(item_price=item_price, rate=rate)

    def _calculate_tax_amount(self, item_price: Decimal, rate: Decimal) -> Decimal:
        tax_amount = (
            item_price * rate / (1 + rate)
            if self.tax_is_included else
            item_price * rate)
        return round(tax_amount, 2)
