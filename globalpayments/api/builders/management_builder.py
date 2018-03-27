from globalpayments.api import ServicesContainer
from globalpayments.api.builders import TransactionBuilder
from globalpayments.api.entities.enums import TransactionModifier, TransactionType
from globalpayments.api.payment_methods import TransactionReference


class ManagementBuilder(TransactionBuilder):
    """
    Used to follow up transactions for the supported
    payment method types.
    """
    _amount = None
    _auth_amount = None
    _currency = None
    _description = None
    _gratuity = None
    _po_number = None
    _reason_code = None
    _tax_amount = None
    _tax_type = None

    @property
    def authorization_code(self):
        if isinstance(self._payment_method, TransactionReference):
            return self._payment_method.auth_code
        return None

    @property
    def client_transaction_id(self):
        if isinstance(self._payment_method, TransactionReference):
            return self._payment_method.client_transaction_id
        return None

    @property
    def order_id(self):
        if isinstance(self._payment_method, TransactionReference):
            return self._payment_method.order_id
        return None

    @property
    def transaction_id(self):
        if isinstance(self._payment_method, TransactionReference):
            return self._payment_method.transaction_id
        return None

    def with_po_number(self, value):
        self._transaction_modifier = TransactionModifier.LevelII
        self._po_number = value
        return self

    def with_tax_amount(self, value):
        self._transaction_modifier = TransactionModifier.LevelII
        self._tax_amount = value
        return self

    def with_tax_type(self, value):
        self._transaction_modifier = TransactionModifier.LevelII
        self._tax_type = value
        return self

    def __init__(self, transaction_type):
        TransactionBuilder.__init__(self, transaction_type)

    def execute(self):
        """
        Executes the builder against the gateway.
        :return: Transaction
        """
        TransactionBuilder.execute(self)

        client = ServicesContainer.instance().get_client()
        return client.manage_transaction(self)

    def setup_validations(self):
        self.validations.of(TransactionType.Capture | TransactionType.Edit |
                            TransactionType.Hold | TransactionType.Release) \
            .check('_transaction_id').is_not_none()

        self.validations.of(TransactionType.Edit).with_constraint(TransactionModifier.LevelII) \
            .check('_tax_type').is_not_none()

        self.validations.of(TransactionType.Refund) \
            .when('_amount').is_not_none() \
            .check('_currency').is_not_none()
