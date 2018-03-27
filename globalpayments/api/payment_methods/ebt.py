import globalpayments as gp
from globalpayments.api.entities.enums import CvnPresenceIndicator, InquiryType, PaymentMethodType, TransactionType


class EBT(object):
    payment_method_type = PaymentMethodType.EBT
    pin_block = None

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
        return gp.api.builders.AuthorizationBuilder(TransactionType.AddValue, self) \
            .with_amount(amount)

    def balance_inquiry(self, inquiry=InquiryType.FoodStamp):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Balance, self) \
            .with_balance_inquiry_type(inquiry) \
            .with_amount(0)

    def benefit_withdrawal(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.BenefitWithdrawal, self) \
            .with_amount(amount)

    def charge(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Sale, self) \
            .with_amount(amount)

    def refund(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Refund, self) \
            .with_amount(amount)

    def reverse(self, amount=None):
        raise NotImplementedError()


class EBTCardData(EBT):
    approval_code = None
    number = None
    exp_month = None
    exp_year = None
    cvn = None
    cvn_presence_indicator = CvnPresenceIndicator.NotRequested
    card_holder_name = None
    card_present = False
    reader_present = False
    serial_number = None


class EBTTrackData(EBT):
    encryption_data = None
    entry_method = None
    value = None
