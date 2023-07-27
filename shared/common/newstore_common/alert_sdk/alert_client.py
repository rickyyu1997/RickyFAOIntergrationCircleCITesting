import boto3
import dataclasses
import json
import logging
import traceback

from .alert import Alert, Event, Error, EventTrigger

from typing import Callable, Any

logger = logging.getLogger(__name__)


class FakeException(Exception):
    pass


class AlertClient:

    def __init__(self, stage: str):
        if stage != "x" and stage != "s" and stage != "p":
            raise ValueError("The stage needs to be 'x' or 's' or 'p' ")
        self.lambda_client = boto3.client('lambda')
        self.stage = stage

    def _format_exception(self, ex: Exception):
        traceback_string = traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__)
        return ''.join(traceback_string)

    def add_alert(self,
                  alert_id: str,
                  event_payload: str,
                  integration_arn: str,
                  event_trigger: EventTrigger,
                  error_message: str,
                  service: str,
                  error_stacktrace: Exception = None,
                  ):

        # If no exception is provided, provide the stacktrace of current
        # execution context
        if error_stacktrace is None:
            stacktrace = ''.join(traceback.format_stack())
        else:
            stacktrace = self._format_exception(error_stacktrace)

        error = Error(
            message=error_message,
            stacktrace=stacktrace
        )
        event = Event(
            trigger=event_trigger,
            payload=event_payload
        )
        alert = Alert(
            alert_id=alert_id,
            event=event,
            error=error,
            integration_arn=integration_arn,
            service=service

        )

        alert_dict = dataclasses.asdict(alert)
        alert_dict["event"]["trigger"] = alert.event.trigger.value
        alert_payload = json.dumps(alert_dict)
        account_id = boto3.client('sts').get_caller_identity().get('Account')
        lambda_name = "arn:aws:lambda:us-east-1:{}:function:" \
                      "alert-bug-service-{}-AddAlert".format(account_id, self.stage)

        return self.lambda_client.invoke(FunctionName=lambda_name, Payload=alert_payload)

    def close_alert(self, alert_id: str):
        alert_payload = json.dumps({"alert_id": alert_id})
        account_id = boto3.client('sts').get_caller_identity().get('Account')
        lambda_name = "arn:aws:lambda:us-east-1:{}:function:" \
                      "alert-bug-service-{}-CloseAlert".format(account_id, self.stage)

        return self.lambda_client.invoke(FunctionName=lambda_name, Payload=alert_payload)
