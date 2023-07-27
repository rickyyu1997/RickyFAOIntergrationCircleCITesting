import re
from dataclasses import dataclass
from typing import Dict, Optional, List
from decimal import Decimal
from newstore_common.sfcc.xml_api.order.address import Address
from newstore_common.sfcc.xml_api.order.common_fields import TextNode, ValuedObject
from newstore_common.sfcc.xml_api.order.line_item import ProductLineItem, ShippingLineItem
from newstore_common.sfcc.xml_api.order.totals import TotalAmount, PriceAdjustment


@dataclass(frozen=True)
class Customer:
    attributes: Dict
    billing_address: Address
    customer_no: Optional[str]
    customer_name: Optional[str]
    customer_email: Optional[str]


@dataclass(frozen=True)
class Status:
    attributes: Dict
    order_status: str
    shipping_status: str
    confirmation_status: str
    payment_status: str


@dataclass(frozen=True)
class ShipmentStatus:
    attributes: Dict
    shipping_status: str


@dataclass(frozen=True)
class ShipmentTotals:
    attributes: Dict
    merchandize_total: TotalAmount
    adjusted_merchandize_total: TotalAmount
    shipping_total: TotalAmount
    adjusted_shipping_total: TotalAmount
    shipment_total: TotalAmount


@dataclass(frozen=True)
class Shipment:
    attributes: Dict
    status: ShipmentStatus
    shipping_method: str
    tracking_number: str
    shipping_address: Address
    gift: str
    totals: ShipmentTotals
    custom_attributes: TextNode


@dataclass(frozen=True)
class Totals:
    attributes: Dict
    merchandize_total: TotalAmount
    adjusted_merchandize_total: TotalAmount
    shipping_total: TotalAmount
    adjusted_shipping_total: TotalAmount
    order_total: TotalAmount


@dataclass(frozen=True)
class PaymentCustomMethod:
    attributes: Dict
    method_name: str


@dataclass(frozen=True)
class GiftCertificate:
    attributes: Dict
    custom_attributes: List[TextNode]
    amount: Decimal


@dataclass(frozen=True)
class ApplePayInfo:
    attributes: Dict


@dataclass(frozen=True)
class Payment:
    attributes: Dict
    custom_method: Optional[PaymentCustomMethod]
    gift_certificate: Optional[GiftCertificate]
    dw_apple_pay: Optional[ApplePayInfo]
    transaction_id: Optional[str]
    amount: Decimal


@dataclass(frozen=True)
class Order:
    attributes: Dict
    order_date: str
    created_by: str
    original_order_no: str
    currency: str
    taxation: str
    invoice_no: str
    customer: Customer
    status: Status
    current_order_no: str
    product_lineitems: List[ProductLineItem]
    shipping_lineitems: List[ShippingLineItem]
    shipments: List[Shipment]
    totals: Totals
    payments: List[Payment]
    custom_attributes: List[TextNode]
    customer_locale: Optional[str]

    @property
    def order_id(self):
        return self.attributes['order-no']

    @property
    def locale(self):
        return 'en-US'

    @property
    def customer_language(self):
        if self.customer_locale:
            return re.split(r'[-_]', self.customer_locale)[0]
        else:
            return 'en'

    @property
    def is_tax_included(self) -> bool:
        return self.price_method == 'tax_included'

    @property
    def price_method(self):
        return ('tax_excluded'
                if self.taxation == 'net' else
                'tax_included')

    @property
    def billing_address(self):
        return self.customer.billing_address

    @property
    def shipping_address(self):
        return self.shipments[0].shipping_address

    @property
    def combined_merchandize_discount(self) -> Optional[PriceAdjustment]:
        if not self.merchandize_discounts:
            return None
        if len(self.merchandize_discounts) == 1:
            return self.merchandize_discounts[0]

        combined_discount_text = {
            'lineitem_text': [],
            'promotion_id': [],
            'campaign_id': []
        }

        combined_discount_values = {
            'attributes': {},
            'tax': Decimal(0),
            'base_price': Decimal(0),
            'tax_basis': Decimal(0),
            'gross_price': Decimal(0),
            'net_price': Decimal(0)
        }

        for discount in self.merchandize_discounts:
            combined_discount_values['tax'] += discount.tax
            combined_discount_values['base_price'] += discount.base_price
            combined_discount_values['tax_basis'] += discount.tax_basis
            combined_discount_values['gross_price'] += discount.gross_price
            combined_discount_values['net_price'] += discount.net_price

            combined_discount_text['lineitem_text'].append(discount.lineitem_text)
            combined_discount_text['promotion_id'].append(discount.promotion_id)
            combined_discount_text['campaign_id'].append(discount.campaign_id)

        joined_discount_text = {key: ', '.join(value)
                                for key, value in combined_discount_text.items()}

        return PriceAdjustment(**combined_discount_values,
                               **joined_discount_text)

    @property
    def merchandize_discounts(self) -> List[PriceAdjustment]:
        if not self.totals.merchandize_total.price_adjustments:
            return []
        else:
            return self.totals.merchandize_total.price_adjustments

    @property
    def total_item_cost(self):
        return round(sum(self.get_price_value(item)
                         for item in self.product_lineitems))

    def get_price_value(self, priced_object: ValuedObject):
        return (priced_object.gross_price
                if self.price_method == 'tax_included' else
                priced_object.net_price)

