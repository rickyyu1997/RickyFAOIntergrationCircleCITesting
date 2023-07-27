from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Address:
    attributes: Dict
    first_name: Optional[str]
    last_name: Optional[str]
    address1: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    country_code: Optional[str]
    phone: Optional[str]
    state: Optional[str]
    address2: Optional[str]

