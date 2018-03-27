"""
"""

import globalpayments as gp
from globalpayments.api.entities.address import Address
from globalpayments.api.entities.batch_summary import BatchSummary
from globalpayments.api.entities.debit_mac import DebitMac
from globalpayments.api.entities.ecommerce_info import ECommerceInfo
from globalpayments.api.entities.encryption_data import EncryptionData
from globalpayments.api.entities.enums import PaymentMethodType, TransactionType
from globalpayments.api.entities.exceptions import ApiException, UnsupportedTransactionException
from globalpayments.api.entities.three_d_secure import ThreeDSecure
from globalpayments.api.entities.transaction_summary import TransactionSummary
from globalpayments.api.payment_methods import TransactionReference
from globalpayments.api.services import RecurringService


class Transaction(object):
    """
    Transaction Response
    """
    authorized_amount = None
    available_balance = None
    avs_response_code = None
    avs_response_message = None
    balance_amount = None
    batch_summary = None
    card_type = None
    card_last_4 = None
    cavv_response_code = None
    commercial_indicator = None
    cvn_response_code = None
    cvn_response_message = None
    emv_issuer_response = None
    points_balance_amount = None
    recurring_data_code = None
    reference_number = None
    response_code = None
    response_message = None
    response_values = {}
    timestamp = None
    transaction_descriptor = None
    token = None
    gift_card = None
    transaction_reference = None

    @property
    def authorization_code(self):
        if self.transaction_reference is not None:
            return self.transaction_reference.auth_code
        return None

    @authorization_code.setter
    def authorization_code(self, value):
        if self.transaction_reference is None:
            self.transaction_reference = TransactionReference()
        self.transaction_reference.auth_code = value

    @property
    def client_transaction_id(self):
        if self.transaction_reference is not None:
            return self.transaction_reference.client_transaction_id
        return None

    @client_transaction_id.setter
    def client_transaction_id(self, value):
        if self.transaction_reference is None:
            self.transaction_reference = TransactionReference()
        self.transaction_reference.client_transaction_id = value

    @property
    def order_id(self):
        if self.transaction_reference is not None:
            return self.transaction_reference.order_id
        return None

    @order_id.setter
    def order_id(self, value):
        if self.transaction_reference is None:
            self.transaction_reference = TransactionReference()
        self.transaction_reference.order_id = value

    @property
    def payment_method_type(self):
        if self.transaction_reference is not None:
            return self.transaction_reference.payment_method_type
        return None

    @payment_method_type.setter
    def payment_method_type(self, value):
        if self.transaction_reference is None:
            self.transaction_reference = TransactionReference()
        self.transaction_reference.payment_method_type = value

    @property
    def transaction_id(self):
        if self.transaction_reference is not None:
            return self.transaction_reference.transaction_id
        return None

    @transaction_id.setter
    def transaction_id(self, value):
        if self.transaction_reference is None:
            self.transaction_reference = TransactionReference()
        self.transaction_reference.transaction_id = value

    @staticmethod
    def from_id(transaction_id,
                payment_method_type=PaymentMethodType.Credit,
                order_id=None):
        """
        Creates a `Transaction` object from a stored transaction ID.
        Used to expose management requests on the original transaction
        at a later date/time.
        :param transaction_id: The original transaction ID
        :param payment_method_type: The original payment method type.
            Defaults to `PaymentMethodType.Credit`.
        :param order_id: The original transaction's order ID
        :return: Transaction
        """
        rvalue = Transaction()
        rvalue.transaction_id = transaction_id
        rvalue.payment_method_type = payment_method_type
        rvalue.order_id = order_id
        return rvalue

    def additional_auth(self, amount=None):
        """
        Creates an additional authorization against the original transaction.
        :param amount: The additional amount to authorize
        :return: ManagementBuilder
        """
        return gp.api.builders.ManagementBuilder(TransactionType.Auth) \
            .with_payment_method(self.transaction_reference) \
            .with_amount(amount)

    def capture(self, amount=None):
        """
        Captures the original transaction.
        :param amount: The amount to capture
        :return: ManagementBuilder
        """
        return gp.api.builders.ManagementBuilder(TransactionType.Capture) \
            .with_payment_method(self.transaction_reference) \
            .with_amount(amount)

    def edit(self):
        """
        Edits the original transaction.
        :return: ManagementBuilder
        """
        return gp.api.builders.ManagementBuilder(TransactionType.Edit) \
            .with_payment_method(self.transaction_reference)

    def hold(self):
        """
        Places the original transaction on hold.
        :return: ManagementBuilder
        """
        return gp.api.builders.ManagementBuilder(TransactionType.Hold) \
            .with_payment_method(self.transaction_reference)

    def refund(self, amount=None):
        """
        Refunds/returns the original transaction.
        :param amount:The amount to refund/return
        :return: ManagementBuilder
        """
        return gp.api.builders.ManagementBuilder(TransactionType.Refund) \
            .with_payment_method(self.transaction_reference) \
            .with_amount(amount)

    def release(self):
        """
        Releases the original transaction from a hold.
        :return: ManagementBuilder
        """
        return gp.api.builders.ManagementBuilder(TransactionType.Release) \
            .with_payment_method(self.transaction_reference)

    def reverse(self, amount=None):
        """
        Reverses the original transaction.
        :param amount: The original authorization amount
        :return: ManagementBuilder
        """
        return gp.api.builders.ManagementBuilder(TransactionType.Reversal) \
            .with_payment_method(self.transaction_reference) \
            .with_amount(amount)

    def void(self):
        """
        Voids the original transaction.
        :return: ManagementBuilder
        """
        return gp.api.builders.ManagementBuilder(TransactionType.Void) \
            .with_payment_method(self.transaction_reference)


class RecurringEntity(object):
    """
    Base implementation for recurring resource types.
    """

    id = None
    key = None

    def create(self, config_name=None):
        """
        Creates a resource
        :return: RecurringEntity
        """

        return gp.api.services.RecurringService.create(self, config_name)

    def delete(self, force=False, config_name=None):
        """
        Delete a record from the gateway.
        :param force: Indicates if the deletion should be forced
        :return: void
        """
        try:
            return gp.api.services.RecurringService.delete(
                self, force, config_name)
        except ApiException as exc:
            raise ApiException(
                'Failed to delete record, see inner exception for more details. ',
                exc)

    @staticmethod
    def find(identifier_name, identifier, config_name=None):
        """
        Searches for a specific record by `id`.
        :param identifier: The ID of the record to find
        :return: RecurringEntity or None if not found
        """
        client = gp.api.ServicesContainer.instance().get_recurring_client(
            config_name)
        if client is not None and client.supports_retrieval:
            response = gp.api.services.RecurringService.search() \
                .add_search_criteria(identifier_name, identifier) \
                .execute(config_name)
            entity = response[0]
            if entity is not None:
                return gp.api.services.RecurringService.get(
                    entity.key, config_name)
            return None
        raise UnsupportedTransactionException()

    @staticmethod
    def find_all(config_name=None):
        """
        Lists all records of base type
        :return: Array
        """
        client = gp.api.ServicesContainer.instance().get_recurring_client(
            config_name)
        if client is not None and client.supports_retrieval:
            return gp.api.services.RecurringService.search().execute(
                config_name)
        raise UnsupportedTransactionException()

    def save_changes(self, config_name=None):
        try:
            return gp.api.services.RecurringService.edit(self, config_name)
        except ApiException as exc:
            raise ApiException(
                'Update failed, see inner exception for more details. ' +
                exc.message, exc)


class Customer(RecurringEntity):
    """
    A customer resource.
    Mostly used in recurring scenarios.
    """

    title = None
    first_name = None
    last_name = None
    company = None
    address = None
    home_phone = None
    work_phone = None
    fax = None
    mobile_phone = None
    email = None
    comments = None
    department = None
    status = None
    payment_methods = None

    def add_payment_method(self, payment_id, payment_method):
        """
        Adds a payment method to the customer
        :param payment_id: An application derived ID for the payment method
        :param payment_method: The payment method
        :return: RecurringPaymentMethod
        """

        name_on_account = ""  # "%s %s".format(self.first_name, self.last_name)
        if not name_on_account:
            name_on_account = self.company

        method = RecurringPaymentMethod(payment_method)
        method.address = self.address
        method.customer_key = self.key
        method.id = payment_id
        method.name_on_account = name_on_account
        return method

    @staticmethod
    def find(identifier, config_name=None):
        RecurringEntity.find('customerIdentifier', identifier, config_name)


class RecurringPaymentMethod(RecurringEntity):
    address = None
    commercial_indicator = None
    customer_key = None
    expiration_date = None
    name_on_account = None
    payment_method = None
    payment_method_type = PaymentMethodType.Recurring
    payment_type = None
    preferred_payment = None
    status = None
    tax_type = None

    def __init__(self, payment_method_or_customer=None, payment_id=None):
        if isinstance(payment_method_or_customer, str):
            self.customer_key = payment_method_or_customer
            self.key = payment_id
            self.payment_type = "Credit Card"
        else:
            self.payment_method = payment_method_or_customer

    def authorize(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Auth, self) \
            .with_amount(amount) \
            .with_one_time_payment(True)

    def charge(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Sale, self) \
            .with_amount(amount) \
            .with_one_time_payment(True)

    def refund(self, amount=None):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Refund, self) \
            .with_amount(amount)

    def verify(self):
        return gp.api.builders.AuthorizationBuilder(TransactionType.Verify,
                                                    self)

    def add_schedule(self, schedule_id):
        data = Schedule()
        data.customer_key = self.customer_key
        data.payment_key = self.key
        data.id = schedule_id
        return data

    @staticmethod
    def find(identifier, config_name=None):
        RecurringEntity.find('paymentMethodIdentifier', identifier,
                             config_name)


class Schedule(RecurringEntity):
    amount = None
    cancellation_date = None
    currency = None
    customer_key = None
    description = None
    device_id = None
    email_notification = None
    email_receipt = None
    end_date = None
    frequency = None
    has_started = False
    invoice_number = None
    name = None
    next_processing_date = None
    number_of_payments = None
    po_number = None
    payment_key = None
    payment_schedule = None
    reprocessing_count = None
    start_date = None
    status = None
    tax_amount = None

    @property
    def total_amount(self):
        return self.amount + self.tax_amount

    def __init__(self, customer_key=None, payment_key=None):
        self.customer_key = customer_key
        self.payment_key = payment_key

    @staticmethod
    def find(identifier, config_name=None):
        RecurringEntity.find('scheduleIdentifier', identifier, config_name)
