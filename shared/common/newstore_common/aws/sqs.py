from typing import Iterable
from typing import Callable

import boto3
import logging

import json
from newstore_common.utils import CachedProperty
from newstore_common.utils.collections import chunk_iterable

logger = logging.getLogger(__name__)


class SQSHandler:

    def __init__(self, queue_name: str):
        self.queue_name = queue_name

    @CachedProperty
    def resource(self):
        sqs = boto3.resource('sqs')
        return sqs.get_queue_by_name(QueueName=self.queue_name)

    def send_batch(self, iterator: Iterable, chunk_size=10):
        for chunk in chunk_iterable(iterator, chunk_size):
            chunk_list = list(chunk)
            logger.info(f"Sending batch to sqs {json.dumps(chunk_list, indent=4)}")
            response = self.resource.send_messages(Entries=chunk_list)
            logger.info(f"got sqs response {response}")

    def send_batch_with_selectors(self, iterator: Iterable,
                                  body_selector: Callable[[any], str],
                                  id_selector: Callable[[any], str]):
        transformed = ({"MessageBody": body_selector(event), "Id": id_selector(event)} for event in iterator)
        self.send_batch(transformed)

    def send_message(self, message_body, delay_seconds=0):
        return self.resource.send_message(
            MessageBody=message_body,
            DelaySeconds=delay_seconds)
