import logging
import json
import traceback

from .alert_client import AlertClient
from .alert import EventTrigger
from typing import Callable, Any

from ..aws.context import FakeAwsContext

logger = logging.getLogger(__name__)


class AlertContext:
    def __init__(self, event_payload, integration_arn, event_trigger=None, alert_id=None,
                 error_message=None, error_stacktrace=None, alert_client=None, service=None, stage=None):
        self.alert_id = alert_id
        self.event_payload = event_payload
        self.integration_arn = integration_arn
        self.event_trigger = event_trigger
        self.error_message = error_message
        self.error_stacktrace = error_stacktrace
        self.alert_client = alert_client
        self.service = service
        self.stage = stage

    def get_id(self):
        return self.alert_id

    def set_service(self, service: str):
        self.service = service

    def set_stage(self, stage: str):
        self.stage = stage
        self._set_alert_client(stage)

    def set_trigger(self, trigger: EventTrigger):
        self.event_trigger = trigger

    def set_id(self, unique_part: str):
        fix = f"{self.service}-{self.stage}"
        if fix in self.alert_id:
            self.alert_id += unique_part
        else:
            self.alert_id = f"{fix}_{self.alert_id}{unique_part}"

    def _set_alert_client(self, stage: str):
        self.alert_client = AlertClient(stage)


# Decorator
def start_alert():
    def wrapper(inner: Callable[[dict, object, AlertContext], Any]) -> Any:
        def wrapper2(raw_data: {}, context: FakeAwsContext) -> Any:
            alert_context = AlertContext(
                event_payload=json.dumps(raw_data),
                integration_arn=context.invoked_function_arn,
                alert_id=f"{context.function_name}_exception_",
            )
            r = ""
            try:
                r = inner(raw_data, context, alert_context)
            except Exception as e:
                logger.info(f"alert handler got exception: {e}")
                alert_context.error_stacktrace = e
                alert_context.error_message = traceback.format_exception_only(type(e), e)[-1]

            if alert_context.error_stacktrace:
                alert_context.alert_client.add_alert(
                    alert_id=alert_context.alert_id,
                    event_payload=alert_context.event_payload,
                    integration_arn=alert_context.integration_arn,
                    event_trigger=alert_context.event_trigger,
                    error_message=alert_context.error_message,
                    error_stacktrace=alert_context.error_stacktrace,
                    service=alert_context.service
                )
                raise alert_context.error_stacktrace
            alert_context.alert_client.close_alert(alert_context.alert_id)
            return r

        return wrapper2

    return wrapper
