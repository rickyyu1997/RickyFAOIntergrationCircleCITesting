import json
import logging
import os
from pathlib import Path

from newstore_common.aws.http import api_status
from newstore_common.enqueuing import Enqueuing
from newstore_common.newstore.events import validate_event_base, NewstoreEvent, create_from_sqs

logger = logging.getLogger(__name__)
logging.basicConfig()


class EnqueuingBuilder:

    def __init__(self):
        self.event = None
        self.config = None
        self.context = None

    def from_ns_event(self, ns_event: NewstoreEvent):
        self.event = ns_event.get_original_dict()

    def from_aws_gateway_event(self, aws_event: {}):
        logger.info(f"Received aws event: {json.dumps(aws_event)}")
        self.event = json.loads(aws_event["body"])

    def with_context(self, context: {}):
        self.context = context

    def with_config(self, config: {}):
        self.config = config

    def create(self) -> Enqueuing:
        queue = self.config["default_queue"]
        return Enqueuing(queue, self.config, self.context)

    def run_gateway(self):
        return enqueue_aws_gateway(self.event, self.config, self.context)


def enqueue_aws_gateway(event_body: {}, enqueuing_config: {}, lambda_parameters: {}, delay_seconds: int = 60):
    (valid, message) = validate_event_base(event_body, enqueuing_config["tenant"])
    if not valid:
        logger.info(f"invalid event {message}")
        return api_status(400, message)

    enqueuing = Enqueuing(enqueuing_config["default_queue"], enqueuing_config, lambda_parameters,
                          delay_seconds=delay_seconds)
    ns_event = NewstoreEvent(event_body)
    logger.info(f"got ns event: {json.dumps(ns_event.get_original_dict(), indent=4)}")
    if not enqueuing.can_queue(ns_event):
        message = f"Event is not configured or enabled and will be ignored: {ns_event.get_name()}"
        logger.info(message)
        return api_status(200, message)

    enqueuing.queue(ns_event)
    message = f"Event was successfully queued {ns_event.get_name()}"
    logger.info(message)
    return api_status(200, message)


def dequeue_sqs_event(aws_event: {}, enqueuing_config: {}, lambda_parameters: {}):
    success, message, ns_event = create_from_sqs(aws_event)

    if not success:
        # todo push directly into dlq
        raise Exception(f"Got invalid event in queue: {message}")

    enqueuing = Enqueuing(enqueuing_config["default_queue"], enqueuing_config, lambda_parameters)

    result = enqueuing.dequeue(ns_event)

    return result
