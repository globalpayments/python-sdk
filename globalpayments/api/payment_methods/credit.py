'''
Credit payment method types
'''

import re
import globalpayments as gp
from globalpayments.api.entities.enums import (
    CvnPresenceIndicator, PaymentMethodType, TransactionType)


class Credit(object):
    '''
    Use credit as a payment method.
    '''

    tokenizable = True

    encryption_data = None
    '''
    The card's encryption data; where applicable.
    '''

    payment_method_type = PaymentMethodType.Credit
    '''
    Set to L{PaymentMethodType.Credit} for internal methods.
    '''

    three_d_secure = None
    '''
    3DSecure data attached to the card
    '''

    token = None
    '''
    A token value representing the card.
    '''

    @property
    def is_card_data(self):
        '''
        Helper method to test if a L{Credit} object is card data.
        '''
        try:
            _number_attr = getattr(self, 'number')
            return True
        except AttributeError as _exc:
            return False

    @property
    def is_track_data(self):
        '''
        Helper method to test if a L{Credit} object is track data.
        '''
        try:
            _number_attr = getattr(self, 'value')
            return True
        except AttributeError as _exc:
            return False

    def add_value(self, amount=None):
        '''
        Adds value to to a payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        '''

        return gp.api.builders.AuthorizationBuilder(TransactionType.AddValue, self) \
            .with_amount(amount)

    def authorize(self, amount=None):
        '''
        Creates an authorization against the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        '''

        currency = None
        order_id = None
        if self.three_d_secure is not None:
            currency = self.three_d_secure.currency
            order_id = self.three_d_secure.order_id

            if amount is None:
                amount = self.three_d_secure.amount

        return gp.api.builders.AuthorizationBuilder(TransactionType.Auth, self) \
            .with_amount(amount) \
            .with_currency(currency) \
            .with_order_id(order_id)

    def charge(self, amount=None):
        '''
        Creates a charge (sale) against the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        '''

        currency = None
        order_id = None
        if self.three_d_secure is not None:
            currency = self.three_d_secure.currency
            order_id = self.three_d_secure.order_id

            if amount is None:
                amount = self.three_d_secure.amount

        return gp.api.builders.AuthorizationBuilder(TransactionType.Sale, self) \
            .with_amount(amount) \
            .with_currency(currency) \
            .with_order_id(order_id)

    def balance_inquiry(self, inquiry=None):
        '''
        Completes a balance inquiry (lookup) on the payment method.

        @type inquiry: L{BalanceInquiryType}
        @param inquiry: The type of inquiry to make
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        '''

        return gp.api.builders.AuthorizationBuilder(TransactionType.Balance, self) \
            .with_balance_inquiry_type(inquiry)

    def refund(self, amount=None):
        '''
        Refunds the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        '''

        return gp.api.builders.AuthorizationBuilder(TransactionType.Refund, self) \
            .with_amount(amount)

    def reverse(self, amount=None):
        '''
        Reverses a previous transaction against the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        '''

        return gp.api.builders.AuthorizationBuilder(TransactionType.Reversal, self) \
            .with_amount(amount)

    def tokenize(self):
        '''
        Tokenizes the payment method, verifying the payment method
        with the issuer in the process.

        @rtype: string
        @return: The requested token
        '''

        response = self.verify() \
            .with_request_multi_use_token(True) \
            .execute()
        return response.token

    def verify(self):
        '''
        Verifies the payment method with the issuer.

        @rtype: L{AuthorizationBuilder}
        @return: The builder
        '''

        return gp.api.builders.AuthorizationBuilder(TransactionType.Verify,
                                                    self)


class CreditCardData(Credit):
    '''
    Use credit tokens or manual entry data as a payment method.
    '''

    _cvn = None
    _number = None
    _regexDict = {
        'Amex': r'^3[47][0-9]{13}$',
        'MC': r'^5[1-5][0-9]{14}$',
        'Visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
        'DinersClub': r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$',
        'EnRoute': r'^(2014|2149)',
        'Discover': r'^6(?:011|5[0-9]{2})[0-9]{12}$',
        'Jcb': r'^(?:2131|1800|35\d{3})\d{11}$',
    }

    card_type = 'Unknown'
    '''
    The card type of the manual entry data.

    Default value is `Unknown`.
    '''

    card_present = False
    '''
    Indicates if the card is present with the merchant at time of payment.

    Default value is `False`.
    '''

    card_holder_name = None
    '''
    The name on the front of the card.
    '''

    cvn_presence_indicator = CvnPresenceIndicator.NotRequested
    '''
    Indicates card verification number (CVN) presence.

    Default value is L{CvnPresenceIndicator.NotRequested}.
    '''

    exp_month = None
    '''
    The card's expiration month.
    '''

    exp_year = None
    '''
    The card's expiration year.
    '''

    reader_present = False
    '''
    Indicates if a card reader was used when accepting the card data.

    Default value is `False`.
    '''

    @property
    def cvn(self):
        '''
        The card's card verification number (CVN).

        When set, L{CreditCardData.cvn_presence_indicator} is set to
        L{CvnPresenceIndicator.Present}.
        '''

        return self._cvn

    @cvn.setter
    def cvn(self, value):
        if value is not None and value != '':
            self._cvn = value
            self.cvn_presence_indicator = CvnPresenceIndicator.Present

    @property
    def number(self):
        '''
        The card's number.
        '''

        return self._number

    @number.setter
    def number(self, value):
        if value is None:
            return

        self._number = value.replace(' ', '').replace('-', '')

        for name in self._regexDict:
            if re.match(self._regexDict[name], self._number) is not None:
                self.card_type = name
                break

    @property
    def short_expiry(self):
        '''
        The card's expiration date in `MMYY` format.
        '''

        month = str(self.exp_month).zfill(2)
        year = str(self.exp_year).zfill(4)[:2]
        return '{}{}'.format(month, year)


class CreditTrackData(Credit):
    '''
    Use credit track data as a payment method.
    '''

    entry_method = None
    '''
    Indicates how the card's track data was obtained.
    '''

    value = None
    '''
    The card's track data.
    '''
