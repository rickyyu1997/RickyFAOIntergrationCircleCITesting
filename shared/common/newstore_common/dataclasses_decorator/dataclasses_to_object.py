import dacite

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any, TypeVar


def _get_object(raw_event: dict, type_v: TypeVar):
    return dacite.from_dict(data_class=type_v, data=raw_event, config=dacite.Config(cast=[Enum]))


# Decorator
def with_json(type_v: TypeVar):
    def wrapper_json(inner: Callable[[dataclass], Any]) -> Any:
        def wrapper(raw_data: {}) -> Any:
            return inner(_get_object(raw_data, type_v))
        return wrapper
    return wrapper_json
