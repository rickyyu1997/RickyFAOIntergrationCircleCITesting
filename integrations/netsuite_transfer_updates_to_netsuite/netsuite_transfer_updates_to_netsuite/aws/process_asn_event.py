# -*- coding: utf-8 -*-
# Copyright (C) 2015, 2016, 2017 NewStore, Inc. All rights reserved.

# Runs startup processes
import netsuite.netsuite_environment_loader # pylint: disable=W0611
import netsuite.api.sale as netsuite_sale
import netsuite.api.transfers as netsuite_transfers
import logging
import os
import json
import asyncio
import netsuite_transfer_updates_to_netsuite.transformers.process_inventory_transfer as pit
import netsuite_transfer_updates_to_netsuite.helpers.sqs_consumer as sqs_consumer
from netsuite_transfer_updates_to_netsuite.helpers.utils import Utils
from zeep.helpers import serialize_object

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
SQS_QUEUE = os.environ['SQS_QUEUE']
EVENT_ID_CACHE = os.environ.get('EVENT_ID_CACHE')
DYNAMO_TABLE = Utils.get_dynamo_table(EVENT_ID_CACHE)
# We will limit this to clearing once per instantiation to limit overhead
Utils.clear_old_events(dynamo_table=DYNAMO_TABLE, days=7)


def handler(_, context):
    """
    Receives event payloads from an SQS queue. The payload is taken from the order
    event stream, detailed here:
        https://apidoc.newstore.io/newstore-cloud/hooks_eventstream.html
    Event Type: inventory_transaction.items_received
    """
    LOGGER.info(f'Beginning queue retrieval...')
    Utils.get_newstore_conn(context)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = sqs_consumer.consume(process_inventory, SQS_QUEUE)
    loop.run_until_complete(task)
    loop.stop()
    loop.close()


async def process_inventory(message):
    LOGGER.info(f"Message to process: \n {json.dumps(message, indent=4)}")
    items_received_event = message['payload']

    if Utils.event_already_received(f"{items_received_event['id']}-{items_received_event['chunk_number']}", DYNAMO_TABLE):
        LOGGER.info("Event was already processed, skipping")
        return True

    if not items_received_event.get('asn_id'):
        LOGGER.warning("The asn_id was not informed in payload, skipping.")
        return True

    nws_store_fulfillment_node = items_received_event['fulfillment_location_id']
    nws_store_location_id = Utils.get_nws_location_id(nws_store_fulfillment_node)
    items_received_event['fulfillment_location_id'] = nws_store_location_id
    store = Utils.get_store(nws_store_location_id)
    if not store:
        raise ValueError(f"Unable to find store with id {nws_store_location_id}")
    LOGGER.info(f"Store retrieved: \n{json.dumps(store, indent=4)}")

    item_fulfillments = await get_item_fulfillments(items_received_event)

    current_item_receipt = {}
    current_inventory_adjustment = None
    for item_fulfillment in item_fulfillments:
        LOGGER.info(f"ItemFulfillment retrieved: \n{json.dumps(serialize_object(item_fulfillment), indent=4, default=Utils.json_serial)}")

        item_receipt, inventory_adjustment = await pit.create_item_receipt(item_fulfillment=item_fulfillment,
                                                                           items_received_event=items_received_event,
                                                                           store=store)
        LOGGER.info(f"Transformed item receipt: {json.dumps(serialize_object(item_receipt), indent=4, default=Utils.json_serial)}")
        if not item_receipt['itemList']['item']:
            LOGGER.info('ItemReceipt without items, continue to the next item fulfillment...')
            continue

        if not current_item_receipt or len(current_item_receipt['itemList']['item']) < len(item_receipt['itemList']['item']):
            current_item_receipt = item_receipt
            current_inventory_adjustment = inventory_adjustment

    is_success = False
    if current_item_receipt:
        LOGGER.info(f"Current item receipt: {json.dumps(serialize_object(current_item_receipt), indent=4, default=Utils.json_serial)}")
        is_success, result = netsuite_transfers.create_item_receipt(current_item_receipt)
        if is_success:
            LOGGER.info("Item Receipt successfully created in NetSuite: \n" \
                        f"{json.dumps(serialize_object(result), indent=4, default=Utils.json_serial)}")
            Utils.mark_event_as_received(f"{items_received_event['id']}-{items_received_event['chunk_number']}", DYNAMO_TABLE)
        else:
            LOGGER.error(f'Error creating Item Receipt in NetSuite: {result}')

        if current_inventory_adjustment:
            await create_inventory_adjustment(current_inventory_adjustment)
    else:
        LOGGER.info("There's no item receipt to be created for this event...")

    return is_success


async def create_inventory_adjustment(current_inventory_adjustment):
    LOGGER.info("Transformed inventory adjustment: \n" \
                f"{json.dumps(serialize_object(current_inventory_adjustment), indent=4, default=Utils.json_serial)}")
    is_success_inv, result_inv = netsuite_transfers.create_inventory_adjustment(current_inventory_adjustment)
    if is_success_inv:
        LOGGER.info("Item Receipt successfully created in NetSuite: \n" \
                    f"{json.dumps(serialize_object(result_inv), indent=4, default=Utils.json_serial)}")
    else:
        LOGGER.error(f'Error creating Item Receipt in NetSuite: {result_inv}')


async def get_item_fulfillments(items_received_event):
    tran_id = items_received_event['shipment_ref']
    if tran_id.startswith('TO'):
        # In this case the ASN was created in NewStore by NewStore after a Transfer Order was fulfilled in NewStore
        # So we need to fetch the Transfer Order from NetSuite and then the ItemFulfillment for that Transfer Order
        LOGGER.info('Handle ASN that was created in NOM by the fulfilling of a Transfer Order in NOM.')
        tran_id = tran_id[:9]
        transfer_order = await get_transfer_order(tran_id=tran_id)
        if not transfer_order:
            raise ValueError(f'Unable to find transferOrder with ID {tran_id}')

        item_fulfillments = await get_item_fulfillment(created_from_id=transfer_order['internalId'])
    else:
        # shipment_ref now contains tracking as well, so we need to extract the tranId
        tran_id = tran_id.split('-')[0].strip()
        item_fulfillments = await get_item_fulfillment(tran_id=tran_id)

    if not item_fulfillments:
        raise ValueError(f'Unable to find itemfulfillment with ID {tran_id}')

    return item_fulfillments


async def get_item_fulfillment(tran_id=None, created_from_id=None):
    if tran_id:
        is_success, response = netsuite_sale.get_transaction_with_tran_id(tran_id)
        response = [response]
    else:
        is_success, response = netsuite_sale.get_item_fulfillment_list(created_from_id)

    if not is_success:
        LOGGER.error(f'Error retrieving item fulfillment: {response}')
        return None
    return response


async def get_transfer_order(tran_id):
    is_success, response = netsuite_sale.get_transaction_with_tran_id(tran_id)
    if not is_success:
        LOGGER.error(f'Error retrieving transfer order: {response}')
        return None
    return response