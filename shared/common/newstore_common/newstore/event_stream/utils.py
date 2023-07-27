import json
import logging

from functools import wraps
from dataclasses import dataclass
from typing import Callable, Any
from decimal import Decimal
from dacite import from_dict, Config
from newstore_common.newstore.event_stream.order_completed import OrderCompleted

from . import OrderCreated, OrderItemsCancelled, ReturnProcessed, FulfillmentRequestItemsCompleted, \
    FulfillmentRequestItemsReadyForHandover
from .payment_refunded import PaymentAccountAmountRefunded
from .refund_request_issued import RefundRequestIssued, RefundRequestIssuedFinal

# This import is only required when using 'with_flask'
try:
    from flask import request
except ImportError:
    pass

logger = logging.getLogger(__name__)


def get_event_class(event_name):
    class_map = {
        'order.created': OrderCreated,
        'order.items_cancelled': OrderItemsCancelled,
        'return.processed': ReturnProcessed,
        'refund_request.issued': RefundRequestIssued,
        'fulfillment_request.items_completed': FulfillmentRequestItemsCompleted,
        'fulfillment_request.items_ready_for_handover': FulfillmentRequestItemsReadyForHandover,
        'order.completed': OrderCompleted,
        'payment_account.amount_refunded': PaymentAccountAmountRefunded,
        # custom events
        'refund_request.issued.final': RefundRequestIssuedFinal
    }
    return class_map[event_name]


# Decorator
def log_event(inner: Callable[[dict, object], Any]) -> Callable[[dict, object], Any]:
    def wrapper(event: {}, context: object) -> Any:
        logger.info(f'Received event {json.dumps(event, indent=4)}')
        return inner(event, context)

    return wrapper


def from_json(event: {}):
    cls = get_event_class(event['name'])
    return from_dict(data_class=cls, data=event, config=get_dacite_config())


def dec_hook(from_value):
    if isinstance(from_value, float):
        return Decimal(str(from_value))
    return Decimal(from_value)


_allowed_ints = [Decimal, int]


def _int_hook(from_value):
    if type(from_value) in _allowed_ints:
        return int(from_value)


_allowed_floats = [int, float]


def _float_hook(from_value):
    if type(from_value) in _allowed_floats:
        return float(from_value)


def _from_eventbridge(raw_event: dict):
    return from_json(raw_event['detail'])


def _from_sqs(raw_event: dict):
    return from_json(json.loads(raw_event["Records"][0]["body"]))


def _from_any(raw_event):
    methods = [_from_eventbridge, _from_sqs]
    for method in methods:
        try:
            return method(raw_event)
        except KeyError:
            continue
    raise Exception(f"No method found to construct event {raw_event}")


# Decorator
def with_eventbridge(method: Callable[[dataclass, object, Any], Any]) -> Any:
    def wrapper(raw_event: {}, context: object, *args) -> Any:
        return method(_from_eventbridge(raw_event), context, *args)

    return wrapper


# Decorator
def with_sqs(method: Callable[[dataclass, object, dict, Any], Any]) -> Any:
    def wrapper(raw_event: {}, context: object, *args) -> Any:
        return method(_from_sqs(raw_event), context, raw_event, *args)

    return wrapper


# Decorator
def with_any(method: Callable[[dataclass, object, dict, Any], Any]) -> Any:
    def wrapper(raw_event: {}, context: object, *args) -> Any:
        return method(_from_any(raw_event), context, raw_event, *args)

    return wrapper


# Decorator
def with_flask(data_class: dataclass) -> Callable[..., Any]:
    def decorator(method: Callable[..., Any]) -> Any:
        @wraps(method)
        def wrapper(*args, **kwargs) -> Any:
            payload = request.get_json(force=True)
            typed_event = from_dict(data_class=data_class, data=payload, config=get_dacite_config())
            return method(typed_event, *args, **kwargs)

        return wrapper

    return decorator


def get_dacite_config():
    return Config(type_hooks={Decimal: dec_hook, int: _int_hook, float: _float_hook})
