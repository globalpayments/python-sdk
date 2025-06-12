from typing import Optional
from dataclasses import dataclass, field


@dataclass
class DebitMac(object):
    transaction_code: Optional[str] = field(default=None)
    transmission_number: Optional[str] = field(default=None)
    bank_response_code: Optional[str] = field(default=None)
    mac_key: Optional[str] = field(default=None)
    pin_key: Optional[str] = field(default=None)
    field_key: Optional[str] = field(default=None)
    trace_number: Optional[str] = field(default=None)
    message_authentication_code: Optional[str] = field(default=None)
