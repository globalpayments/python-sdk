"""
"""

from globalpayments.api.entities.enums import EntryMethod


class PaymentMethod(object):
    payment_method_type = None


class CardData(object):
    card_present = False
    cvn = None
    cvn_presence_indicator = None
    number = None
    exp_month = None
    exp_year = None
    reader_present = False


class TrackData(object):
    value = None
    entry_method = EntryMethod.Swipe


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


class Encryptable(object):
    encryption_data = None


class PinProtected(object):
    pin_block = None


class PrePayable(object):
    def add_value(self, amount=None):
        pass


class Refundable(object):
    def refund(self, amount=None):
        pass


class Reversable(object):
    def reverse(self, amount=None):
        pass


class Tokenizable(object):
    token = None

    def tokenize(self):
        pass


class Verifiable(object):
    def verify(self):
        pass