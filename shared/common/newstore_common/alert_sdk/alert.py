from dataclasses import dataclass
from enum import Enum
from newstore_common.aws import init_root_logger

init_root_logger(__name__)


class EventTrigger(Enum):
    SQS = "SQS"
    EVENTBRIDGE = "EVENTBRIDGE"
    SNS = "SNS"
    S3 = "S3"
    API_GATEWAY = "API_GATEWAY"


@dataclass(frozen=True)
class Event:
    payload: str
    trigger: EventTrigger


@dataclass(frozen=True)
class Error:
    message: str
    stacktrace: str


@dataclass(frozen=True)
class Alert:
    alert_id: str
    event: Event
    integration_arn: str
    service: str
    error: Error

