import logging
import json
from typing import Iterable

from newstore_adapter.connector import NewStoreConnector
from newstore_common.aws.sqs import SQSHandler
from newstore_common.newstore import create_ns_connector_from_context
from newstore_common.newstore.events import NewstoreEvent
from newstore_common.utils import CachedProperty

logger = logging.getLogger(__name__)
logging.basicConfig()


class HandlerBase:

    def __init__(self, context: dict):
        self.context = context

    @CachedProperty
    def connector(self) -> NewStoreConnector:
        return create_ns_connector_from_context(self.context)

    def handle(self, event: NewstoreEvent):
        raise NotImplemented()


class Enqueuing:

    def __init__(self, queue_name: str, config: dict, context: dict, handler: SQSHandler = None, delay_seconds: int = 60):
        self.delay_seconds = delay_seconds
        self.context = context
        self.queue_name = queue_name
        self.configuration = config
        if not handler:
            handler = SQSHandler(queue_name)
        self.handler = handler

    def get_config(self, ns_event: NewstoreEvent):
        event_name = ns_event.get_name()
        return self.configuration[event_name] if event_name in self.configuration else None

    def can_queue(self, ns_event: NewstoreEvent) -> bool:
        config = self.get_config(ns_event)
        return config and config["enabled"] is True

    def queue(self, ns_event: NewstoreEvent):
        if not self.can_queue(ns_event):
            raise Exception(f"Event is not allowed to be queued: {ns_event.get_name()}")
        response = self.handler.send_message(message_body=json.dumps(ns_event.get_original_dict()),
                                             delay_seconds=self.delay_seconds)
        logger.info(f"got sqs response {json.dumps(response, indent=4)}")

    def queue_batch(self, iterator: Iterable[NewstoreEvent], id_selector):
        transformed = ({"MessageBody": json.dumps(event.get_original_dict()), "Id": id_selector(event)} for event in
                       iterator)
        # do not validate events, we can do this on deq
        return self.handler.send_batch(transformed)

    def can_dequeue(self, ns_event):
        return self.can_queue(ns_event)

    def dequeue(self, ns_event: NewstoreEvent):
        if not self.can_dequeue(ns_event):
            raise Exception(f"Event cannot be dequeued : {ns_event.get_name()}")
        config = self.get_config(ns_event)

        logger.info(f"got handler config {config}")

        handler = config["handler"](self.context)
        logger.info(f"got handler: {handler}")
        result = handler.handle(ns_event)
        return result
