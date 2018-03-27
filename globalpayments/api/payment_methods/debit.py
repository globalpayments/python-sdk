'''
Credit payment method types
'''

import re
import globalpayments as gp
from globalpayments.api.entities.enums import (
    CvnPresenceIndicator, PaymentMethodType, TransactionType)


class DebitTrackData(object):
    encryption_data = None
    payment_method_type = PaymentMethodType.Debit
    pin_block = None
    value = None

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

    def charge(self, amount=None):
        '''
        Creates a charge (sale) against the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        '''

        order_id = None

        return gp.api.builders.AuthorizationBuilder(TransactionType.Sale, self) \
            .with_amount(amount)

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
