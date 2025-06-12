"""
"""

from dataclasses import dataclass, field
from typing import Optional, Any

from globalpayments.api.entities.enums import EntryMethod


@dataclass
class PaymentMethod(object):
    payment_method_type: Optional[Any] = field(default=None)


@dataclass
class CardData(object):
    card_present: bool = field(default=False)
    cvn: Optional[str] = field(default=None)
    cvn_presence_indicator: Optional[Any] = field(default=None)
    number: Optional[str] = field(default=None)
    exp_month: Optional[str] = field(default=None)
    exp_year: Optional[str] = field(default=None)
    reader_present: bool = field(default=False)


@dataclass
class TrackData(object):
    value: Optional[Any] = field(default=None)
    entry_method: EntryMethod = field(default=EntryMethod.Swipe)


class Authable(object):
    def authorize(self, amount=None):
        pass


class Chargable(object):
    def charge(self, amount=None):
        pass


class Balanceable(object):
    def balance_inquiry(self, inquiry_type=None):
        pass


class Editable(object):
    def edit(self, amount=None):
        pass


@dataclass
class Encryptable(object):
    encryption_data: Optional[Any] = field(default=None)


@dataclass
class PinProtected(object):
    pin_block: Optional[Any] = field(default=None)


class PrePayable(object):
    def add_value(self, amount=None):
        pass


class Refundable(object):
    def refund(self, amount=None):
        pass


class Reversable(object):
    def reverse(self, amount=None):
        pass


@dataclass
class Tokenizable(object):
    token: Optional[Any] = field(default=None)

    def tokenize(self):
        pass


class Verifiable(object):
    def verify(self):
        pass
