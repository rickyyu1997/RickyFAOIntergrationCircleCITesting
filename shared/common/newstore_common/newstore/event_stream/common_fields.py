from dataclasses import dataclass


@dataclass(frozen=True)
class ExtendedAttribute:
    name: str
    value: str
