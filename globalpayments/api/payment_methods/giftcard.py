import globalpayments as gp
from globalpayments.api.entities.enums import AliasAction, PaymentMethodType, TransactionType
from globalpayments.api.entities.exceptions import ApiException


class GiftCard(object):
    payment_method_type = PaymentMethodType.Gift
    pin = None
    value_type = None
    value = None

    @property
    def alias(self):
        return self.value

    @alias.setter
    def alias(self, value):
        self.value = value
        self.value_type = 'Alias'

    @property
    def number(self):
        return self.value

    @number.setter
    def number(self, value):
        self.value = value
        self.value_type = 'CardNbr'

    @property
    def token(self):
        return self.value

    @token.setter
    def token(self, value):
        self.value = value
        self.value_type = 'TokenValue'

    @property
    def track_data(self):
        return self.value

    @track_data.setter
    def track_data(self, value):
        self.value = value
        self.value_type = 'TrackData'

    @staticmethod
    def create(alias=None, config_name='default'):
        card = GiftCard()

        try:
            response = gp.api.builders.AuthorizationBuilder(TransactionType.Alias, card) \
                .with_alias(AliasAction.Create, alias) \
                .execute(config_name)

            if response.response_code == '00':
                return response.gift_card

            raise ApiException(response.response_message)
        except Exception:
            raise ApiException('Unable to create gift card alias')

    def add_alias(self, alias=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Alias, self) \
            .with_alias(AliasAction.Add, alias)

    def activate(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Activate, self) \
            .with_amount(amount)

    def add_value(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.AddValue, self) \
            .with_amount(amount)

    def balance_inquiry(self, inquiry=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Balance, self) \
            .with_balance_inquiry_type(inquiry)

    def charge(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Sale, self) \
            .with_amount(amount)

    def deactivate(self):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Deactivate,
                                                    self)

    def remove_alias(self, alias=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Alias, self) \
            .with_alias(AliasAction.Delete, alias)

    def replace_with(self, new_card=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Replace, self) \
            .with_replacement_card(new_card)

    def reverse(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Reversal, self) \
            .with_amount(amount)

    def rewards(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Reward, self) \
            .with_amount(amount)
