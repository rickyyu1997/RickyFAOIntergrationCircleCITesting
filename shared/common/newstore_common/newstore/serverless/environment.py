from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class Stage(IntEnum):
    x = 1
    s = 2
    p = 3


@dataclass(frozen=True)
class NewStoreServerlessEnvironment:
    tenant: str
    stage: Stage
    api_user: str
    api_credentials: str
    function_name: Optional[str]
    function_version: Optional[str]
    request_id: Optional[str]
