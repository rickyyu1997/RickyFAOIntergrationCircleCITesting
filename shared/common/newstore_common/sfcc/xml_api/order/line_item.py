from dataclasses import dataclass
from typing import Dict, List
from decimal import Decimal
from newstore_common.sfcc.xml_api.order.common_fields import TextNode, ValuedObject
from newstore_common.sfcc.xml_api.order.totals import PriceAdjustment


@dataclass(frozen=True)
class LineItem(ValuedObject):
    attributes: Dict
    tax: Decimal
    base_price: Decimal
    lineitem_text: str
    tax_basis: Decimal
    item_id: str
    shipment_id: str
    tax_rate: Decimal
    price_adjustments: List[PriceAdjustment]


@dataclass(frozen=True)
class ShippingLineItem(LineItem):
    pass


@dataclass(frozen=True)
class ProductLineItem(LineItem):
    position: int
    product_id: str
    product_name: str
    quantity: Decimal
    gift: bool
    custom_attributes: TextNode
