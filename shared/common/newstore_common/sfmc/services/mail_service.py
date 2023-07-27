import json
import logging

from mcm_sfmc.handlers import get_order_or_throw, get_customer_order_or_throw
from newstore_adapter.connector import NewStoreConnector
from newstore_common.mapping import map_dict
from newstore_common.newstore.events import NewstoreEvent
from newstore_common.sfmc.api import MessagingApi, Sender
from newstore_common.sfmc.services.mapping import MappingProvider

logger = logging.getLogger(__name__)
logging.basicConfig()


class MailService:

    def __init__(self, connector: NewStoreConnector, mapping_provider: MappingProvider, api: MessagingApi,
                 sender: Sender = None):
        self.connector = connector
        self.sender = sender
        self.api = api
        self.mapping_provider = mapping_provider

    def send(self, event_key: str, order_id: str, event: NewstoreEvent, fields_hook, can_handle=None, endpoint='OrderStatus', recipient_email=None):
        if not self.mapping_provider.has_definition(event_key):
            logger.info(f"skipping event since it is not configured {event_key}")
            return

        customer_order = get_customer_order_or_throw(self.connector, order_id)["customer_order"]
        if recipient_email:
            recipient = recipient_email
        else:
            recipient = customer_order["consumer"]["email"]

        order = self.connector.get_external_order(order_id, id_type="id")
        if not order:
            raise Exception(f"Order does not exist: {order_id}")

        fields = {
            "order": order,
            "event": event.get_payload(),
            "customer_order": customer_order
        }
        if can_handle:
            logger.info(f"Handler registered a can_handle method. Calling can_handle with fields")
            if not can_handle(fields):
                logger.info(f"Can handle method returned false, skipping service")
                return

        event_fields = fields_hook(fields)

        definition = self.mapping_provider.get_definition(event_key)

        logger.info(f"Got fields: {definition.fields}")
        logger.info(f"Got NewStore fields {json.dumps(event_fields, indent=4)}")

        message_fields = map_dict(definition.fields, event_fields)

        # logger.info(f"mapped fields {json.dumps(message_fields, indent=4)}")
        self.api.send(definition.template_id, self.sender, recipient, message_fields, endpoint)
