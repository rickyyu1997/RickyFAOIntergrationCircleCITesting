import json
import logging
from typing import TypeVar, Iterable, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig()


class NewstoreEvent:

    def __init__(self, ns_event):
        self.ns_event = ns_event

    def get_payload(self):
        return self.ns_event["payload"]

    def get_tenant(self):
        return self.ns_event["tenant"]

    def get_name(self):
        return self.ns_event["name"]

    def get_original_dict(self):
        return self.ns_event


class EventBuilder:

    def __init__(self, payload: {}, tenant: str, name: str, published_at: str = None):
        self.tenant = tenant
        self.name = name
        self.payload = payload
        if published_at is None:
            published_at = datetime.now().isoformat()
        self.published_at = published_at

    def build(self) -> NewstoreEvent:
        ns_dict = {
            "payload": self.payload,
            "tenant": self.tenant,
            "name": self.name,
            "published_at": self.published_at
        }
        return NewstoreEvent(ns_dict)


def create_from_sqs(sqs_event) -> Tuple[bool, str, Optional[NewstoreEvent]]:
    logger.info(f"Received sqs event: {sqs_event}")
    newstore_event = json.loads(sqs_event["Records"][0]["body"])
    logger.info(
        f"received newstore event:  {json.dumps(newstore_event, indent=4)}")
    (result, message) = validate_event_dict(newstore_event)
    if not result:
        return False, message, None
    return True, "success", NewstoreEvent(newstore_event)


def validate_event_dict(newstore_event: dict):
    if not (newstore_event.get("tenant") and newstore_event.get("name") and newstore_event.get(
            "published_at") and newstore_event.get("payload")):
        status_message = "Invalid event stream data. Missing attribute(s) [tenant|name|published_at|payload]"
        return False, status_message
    return True, ""


def create_and_validate_event(lambda_event, expected_tenant: str, expected_event: str):
    logger.info(f"received lambda event: {lambda_event}")
    newstore_event = json.loads(lambda_event["Records"][0]["body"])
    logger.info(
        f"received newstore event:  {json.dumps(newstore_event, indent=4)}")
    (success, message) = validate_event(
        newstore_event, expected_tenant, expected_event)
    if not success:
        newstore_event = None
    return success, message, newstore_event


def validate_event_base(newstore_event, expected_tenant: str):
    if not (newstore_event.get("tenant") and newstore_event.get("name") and newstore_event.get(
            "published_at") and newstore_event.get("payload")):
        status_message = "Invalid event stream data. Missing attribute(s) [tenant|name|published_at|payload]"
        return False, status_message

    newstore_tenant = newstore_event.get("tenant").strip().lower()
    if newstore_tenant != expected_tenant.strip().lower():
        status_message = f'Invalid tenant. expected: {expected_tenant}, got: {newstore_tenant}'
        return False, status_message

    return True, ""


def validate_event(newstore_event, expected_tenant: str, expected_event: str):
    (result, message) = validate_event_base(newstore_event, expected_tenant)
    if not result:
        return False, message

    newstore_event = newstore_event.get("name").strip().lower()
    if newstore_event != expected_event.strip().lower():
        status_message = f'invalid event. expected: {expected_event}, got: {newstore_event}'
        return False, status_message
    return True, ""
