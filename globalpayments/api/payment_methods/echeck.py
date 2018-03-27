'''
ACH/eCheck payment method types
'''

import globalpayments as gp
from globalpayments.api.entities.enums import PaymentMethodType, TransactionType


class ECheck(object):
    '''
    Use ACH/eCheck as a payment method.
    '''

    account_number = None
    account_type = None
    ach_verify = None
    birth_year = None
    check_holder_name = None
    check_name = None
    check_number = None
    check_type = None
    check_verify = None
    drivers_license_number = None
    drivers_license_state = None
    entry_mode = None
    micr_number = None
    payment_method_type = None
    phone_number = None
    routing_number = None
    sec_code = None
    ssn_last_4 = None
    token = None

    payment_method_type = PaymentMethodType.ACH
    '''
    Set to L{PaymentMethodType.ACH} for internal methods.
    '''

    def charge(self, amount=None):
        '''
        Creates a charge (sale) against the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        '''

        return gp.api.builders.AuthorizationBuilder(TransactionType.Sale, self) \
            .with_amount(amount)
