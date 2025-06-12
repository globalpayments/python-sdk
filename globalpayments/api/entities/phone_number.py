from typing import Optional
from dataclasses import dataclass, field

from globalpayments.api.entities.enums import PhoneNumberType


@dataclass
class PhoneNumber:
    country_code: Optional[str] = field(default=None)
    number: Optional[str] = field(default=None)
    type: Optional[PhoneNumberType] = field(default=None)
