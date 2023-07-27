from dataclasses import dataclass


@dataclass(frozen=True)
class PayloadFile:
    encoding: str
    content: str
    content_type: str
