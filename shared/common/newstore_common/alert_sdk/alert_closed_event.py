import logging

from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AlertClosedEvent:
    tenant: str
    name: str
    published_at: str
    payload: dict
