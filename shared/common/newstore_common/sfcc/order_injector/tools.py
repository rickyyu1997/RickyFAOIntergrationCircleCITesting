from newstore_common.newstore.api.fulfill_order import NewStoreDiscount
from newstore_common.sfcc.xml_api.order.common_fields import ValuedObject
from newstore_common.sfcc.xml_api.order.totals import PriceAdjustment


def format_discount(
        price_adjustment: PriceAdjustment,
        is_tax_included: bool,
        override_amount=None) -> NewStoreDiscount:
    override_amount = abs(
        get_price(price_adjustment, is_tax_included)
        if override_amount is None else
        override_amount)

    return NewStoreDiscount(
        discount_ref=truncate_string(price_adjustment.promotion_id, max_length=255),
        description=truncate_string(price_adjustment.lineitem_text, max_length=1023),
        type='fixed',
        original_value=round(override_amount, 2),
        price_adjustment=round(override_amount, 2),
        coupon_code=price_adjustment.coupon_id)


def get_price(priced_object: ValuedObject, tax_is_included):
    if tax_is_included:
        return priced_object.gross_price
    else:
        return priced_object.net_price


def truncate_string(string: str, max_length: int):
    return (string[:max_length]
            if len(string) <= max_length else
            string[:max_length-3] + '...')
