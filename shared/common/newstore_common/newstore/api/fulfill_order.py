from decimal import Decimal
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class NewStoreAddress:
    first_name: str
    last_name: str
    country: str
    zip_code: str
    city: str
    address_line_1: str
    state: str
    phone: str
    address_line_2: str


@dataclass(frozen=True)
class NewStoreTaxLine:
    amount: Decimal
    rate: Decimal


@dataclass(frozen=True)
class NewStoreItemPrice:
    item_price: Decimal
    item_list_price: Decimal
    item_tax_lines: List[NewStoreTaxLine]


@dataclass(frozen=True)
class NewStoreDiscount:
    coupon_code: str
    discount_ref: str
    description: str
    original_value: Decimal
    price_adjustment: Decimal
    type: str


@dataclass(frozen=True)
class NewStoreItem:
    external_item_id: str
    product_id: str
    price: NewStoreItemPrice
    item_discount_info: List[NewStoreDiscount]
    item_order_discount_info: List[NewStoreDiscount]


@dataclass(frozen=True)
class NewStoreShippingOption:
    service_level_identifier: str
    display_name: str
    fulfillment_node_id: str
    shipping_type: str
    zip_code: str
    country_code: str
    carrier: str
    price: Decimal
    tax: Decimal
    discount_info: List[NewStoreDiscount]


@dataclass(frozen=True)
class NewStoreShipment:
    items: List[NewStoreItem]
    shipping_option: NewStoreShippingOption


@dataclass(frozen=True)
class NewStorePayment:
    processor: str
    correlation_ref: str
    type: str
    amount: Decimal
    method: str
    processed_at: str


@dataclass(frozen=True)
class NewStoreOrder:
    external_id: str
    placed_at: str
    shop: str
    channel_type: str
    channel_name: str
    currency: str
    customer_name: str
    customer_email: str
    shop_locale: str
    customer_language: str
    is_preconfirmed: bool
    is_historical: bool
    external_customer_id: str
    shipping_address: NewStoreAddress
    billing_address: NewStoreAddress
    shipments: List[NewStoreShipment]
    payments: List[NewStorePayment]
    price_method: str
