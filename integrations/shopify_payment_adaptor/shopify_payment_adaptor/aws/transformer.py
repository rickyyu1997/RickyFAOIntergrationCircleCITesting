import json
import logging

from shopify_payment_adaptor.helpers.product_id_mapper.src.product_id_mapper.main \
    import ProductIdMapper

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

PRODUCT_ID_MAPPER = ProductIdMapper()

async def parse_json_to_calculate_refund(ns_return, shopify_order, ns_order=None, is_exchanged=False):
    """
    Convert NewStore Json of return items and Shopify Json of order to Shopify Calculate Refund Json
    :param ns_return:
    :param shopify_order:
    :return response: dict
    """
    LOGGER.info('Parse json to calculate refund')
    LOGGER.debug(f'ns_return: \n${json.dumps(ns_return, indent=4)}')
    LOGGER.debug('shopify_order: \n${json.dumps(shopify_order, indent=4)}')
    if ns_order:
        LOGGER.debug('ns_order: \n${json.dumps(ns_order, indent=4)}')

    output = {
        "refund": {
            "refund_line_items": []
            }
        }
    if not ns_return:
        ns_return = {}

    if ns_return.get('is_reduction', False) or is_exchanged:
        return output

    refund_line_items = await _get_refund_line_items(ns_return, shopify_order)
    check_already_refunded_items(refund_line_items, shopify_order)
    output['refund']['refund_line_items'] = refund_line_items
    return output


def check_already_refunded_items(refund_line_items, shopify_order):
    refundable = {}
    for refund in shopify_order.get('refunds', []):
        for refunded_line_item in refund['refund_line_items']:
            sub_quant = refunded_line_item['line_item']['quantity'] - refunded_line_item['quantity']
            if refunded_line_item['line_item_id'] in refundable:
                refundable[refunded_line_item['line_item_id']] -= sub_quant
            else:
                refundable[refunded_line_item['line_item_id']] = sub_quant

    for refund_line_item in refund_line_items:
        if refund_line_item['line_item_id'] in refundable \
                and refundable[refund_line_item['line_item_id']] < refund_line_item['quantity']:
            refund_line_item['quantity'] = refundable[refund_line_item['line_item_id']]


async def parse_json_to_create_refund(calculated_refund, ns_return, shopify_order, refund_line_items, amount_info):
    """
    Convert Shopify Json of calculated refund and Newstore return Json
    :param calculated_refund:
    :param ns_return:
    :param shopify_order:
    :param refund_line_items: an array of line_items as generated by `parse_json_to_calculate_refund()`
    :return response: dict
    """
    LOGGER.info('Parse json to create refund')
    LOGGER.debug(json.dumps(calculated_refund, indent=4))
    LOGGER.debug(json.dumps(ns_return, indent=4))
    LOGGER.debug(json.dumps(shopify_order, indent=4))
    LOGGER.debug(json.dumps(amount_info, indent=4))

    output = {
        "refund": {
            "note": "Newstore originated refund",
            "notify": True,            # Got from Document "Shopify payment processor"
            "shipping": {
                "full_refund": await verify_full_return(ns_return, shopify_order)
            },
            "refund_line_items": refund_line_items,
            "transactions": [
                {
                    "parent_id": calculated_refund['refund']['transactions'][0]['parent_id'],
                    "amount": amount_info.get('amount'),
                    "kind": "refund",
                    "gateway": calculated_refund['refund']['transactions'][0]['gateway']
                }
            ]
        }
    }
    return output


async def create_shopify_refund_body(refund_amount, shopify_parent_transaction_id):
    """
    Creates an Shopify transaction object used to perform appeasement refunds
    :param refund_amount:
    :param shopify_parent_transaction_id:
    :return response: dict
    """
    LOGGER.info('Create Shopify refund transaction')

    output = {
        "transaction": {
            "amount": refund_amount,
            "kind": "refund",
            "parent_id": shopify_parent_transaction_id
        }
    }
    return output


async def verify_full_return(ns_return, shopify_order):
    """
    Verify if all items were returned
    :param ns_return:
    :param shopify_order:
    :return True or False
    """
    items_quantity_return = await _get_ns_return_items_quantity(ns_return)
    items_quantity_order = await _get_shopify_items_quantity(shopify_order, items_quantity_return)
    if len(items_quantity_return) == len(items_quantity_order):
        for key in items_quantity_return:
            if items_quantity_order[key]['quantity'] > items_quantity_return[key]:
                return False
        return True
    return False


async def _get_refund_line_items(ns_return, shopify_order):
    """
    Parse information from shopify_order and ns_return to get the refund_line_itens
    :param ns_return:
    :param shopify_order:
    :return array
    """
    output = []
    items_quantity_return = await _get_ns_return_items_quantity(ns_return)
    items_quantity_order = await _get_shopify_items_quantity(shopify_order, items_quantity_return)

    if all_products_returned(ns_return, shopify_order):
        return list(items_quantity_order.values())

    for key in items_quantity_return:
        output.append(items_quantity_order[key])
    return output


async def _get_ns_return_items_quantity(ns_return):
    """
    Extract productId and calculate quantity from ns return
    :param ns_return:
    :return response: dict of productId and quantity returned
    e.g. {'SKU001':2}
    """
    output = {}
    if ns_return:
        for item in ns_return.get('return_items', []):
            if item['product_id'] in output.keys():
                output[item['product_id']] += 1
            else:
                output[item['product_id']] = 1

    return output


async def _get_shopify_items_quantity(shopify_order, items_quantity_return, external_key='sku'):
    """
    Extract product sku and quantity from shopify order
    :param shopify_order:
    :param items_quantity_return: ns return
    :param external_key: the key of the unique id with which to map the shopify line_item to the ns product_id
    :return response: dict of product sku and quantity returned
    e.g. {'SKU001':{'line_item_id':100001, 'quantity':2},'SKU002':{'line_item_id':100001, 'quantity':1}}
    """
    output = {}
    for item in shopify_order['line_items']:
        external_id = _get_product_id_map_from_sku(str(item[external_key]))
        if external_id in items_quantity_return:
            output[external_id] = {
                'line_item_id': item['id'],
                'quantity': items_quantity_return[external_id],
                'restock_type': 'no_restock'
            }
    return output


async def _get_value_with_key(items, key):
    for item in items:
        if item['key'] == key:
            return item['value']


def _get_extended_attribute(extended_attributes, key):
    if extended_attributes:
        for attr in extended_attributes:
            if attr['name'] == key:
                return attr['value']
    return ''


def _get_product_id_map_from_sku(sku):
    product_mapped = PRODUCT_ID_MAPPER.get_map('sku', sku)
    if not product_mapped:
        error_message = f'Could not map sku: {sku} to a product_id.'
        LOGGER.error(error_message)
        raise Exception(error_message)
    return product_mapped['product_id']

def all_products_returned(ns_return, shopify_order):
    """
    Verify if all products were returned
    :param ns_return:
    :param shopify_order:
    :return True or False
    """
    count_shopify_items = sum([item['quantity'] for item in shopify_order['line_items']])
    count_returned_items = len(ns_return.get('return_items', []))

    return count_shopify_items == count_returned_items
