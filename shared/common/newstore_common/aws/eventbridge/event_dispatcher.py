import dataclasses
import json
import logging
from datetime import datetime
from typing import Generic, TypeVar
import boto3
from newstore_common.json.decimal_encoder import DecimalToStringEncoder

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclasses.dataclass(frozen=True)
class Event(Generic[T]):
    payload: T
    time: str = datetime.utcnow().isoformat()
    source: str = 'NewStore'
    version: str = '0'


class AwsEventDispatcher:
    def __init__(self, event_bus_name):
        self.event_bus_name = event_bus_name

    def dispatch(self, event: Event):
        aws_event = self._format_event(event)
        logger.info(
            f'Sending aws event: {json.dumps(aws_event, indent=4, cls=DecimalToStringEncoder)}')
        logger.info(f"With payload: {json.dumps(dataclasses.asdict(event.payload), indent=4, cls=DecimalToStringEncoder)}")
        boto3_client = boto3.client('events')
        response = boto3_client.put_events(Entries=[aws_event])
        _verify_response(response)
        return response

    def _format_event(self, event: Event):
        return {
            'Source': event.source,
            'Time': event.time,
            'DetailType': "NewStoreEventbridgeConnector " + event.version,
            'Detail': json.dumps(dataclasses.asdict(event.payload), cls=DecimalToStringEncoder),
            'EventBusName': self.event_bus_name
        }


# Change to return 502 bad gateway?
def _verify_response(response):
    failed_entry = response["FailedEntryCount"]
    if failed_entry:
        logger.info(json.dumps(response, indent=4))
        raise Exception("Response had a 'FailedEntryCount' that was non-zero")
