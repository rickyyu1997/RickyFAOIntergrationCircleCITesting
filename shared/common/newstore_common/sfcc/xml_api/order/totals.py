from dataclasses import dataclass
from typing import List, Dict
from decimal import Decimal
from newstore_common.sfcc.xml_api.order.common_fields import ValuedObject


@dataclass(frozen=True)
class PriceAdjustment(ValuedObject):
    attributes: Dict
    tax: Decimal
    base_price: Decimal
    lineitem_text: str
    tax_basis: Decimal
    promotion_id: str
    campaign_id: str
    coupon_id: str = ''


@dataclass(frozen=True)
class PriceAdjustments:
    attributes: Dict
    price_adjustment: List[PriceAdjustment]


@dataclass(frozen=True)
class TotalAmount(ValuedObject):
    attributes: Dict
    tax: Decimal
    price_adjustments: List[PriceAdjustment]

