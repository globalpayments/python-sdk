"""
"""

from globalpayments.api import ServicesContainer
from globalpayments.api.builders.validations import Validations
from globalpayments.api.entities import (
    Address,
    TransactionReference,
)
from globalpayments.api.entities.enums import (
    AddressType,
    PaymentMethodType,
    ReportType,
    TransactionModifier,
    TransactionType,
)
from globalpayments.api.entities.exceptions import BuilderException
from globalpayments.api.payment_methods import EBTCardData


class BaseBuilder(object):
    validations = None

    def __init__(self):
        self.validations = Validations()
        self.setup_validations()

    def __getattr__(self, name):
        def wrapper(*args):
            if name[:5] == 'with_':
                self.set_property_if_exists(name[5:], args[0])
                return self

            return False

        return wrapper

    def execute(self, config_name=None):
        self.validations.validate(self)
        return None

    def setup_validations(self):
        pass

    def set_property_if_exists(self, *args):
        if hasattr(self, args[0]):
            setattr(self, args[0], args[1])
        else:
            raise BuilderException('Unknown property {}'.format(args[0]))


class TransactionBuilder(BaseBuilder):
    transaction_type = None
    transaction_modifier = None
    payment_method = None

    def __init__(self, transaction_type, payment_method=None):
        BaseBuilder.__init__(self)
        self.transaction_type = transaction_type
        self.payment_method = payment_method


class AuthorizationBuilder(TransactionBuilder):
    """
    Used to create charges, verifies, etc. for the supported
    payment method types.
    """

    account_type = None
    alias = None
    alias_action = None
    allow_duplicates = None
    allow_partial_auth = None
    amount = None
    auth_amount = None
    balance_inquiry_type = None
    billing_address = None
    cash_back_amount = None
    chip_condition = None
    client_transaction_id = None
    currency = None
    customer_id = None
    customer_ip_address = None
    cvn = None
    description = None
    dynamic_descriptor = None
    ecommerce_info = None
    gratuity = None
    convenience_amt = None
    shipping_amt = None
    hosted_payment_data = None
    invoice_number = None
    level_2_request = None
    message_authentication_code = None
    offline_auth_code = None
    one_time_payment = False
    order_id = None
    pos_sequence_number = None
    product_id = None
    recurring_sequence = None
    recurring_type = None
    request_multi_use_token = False
    replacement_card = None
    schedule_id = None
    shipping_address = None
    timestamp = None

    def with_address(self, address, address_type=AddressType.Billing):
        if not isinstance(address, Address):
            raise BuilderException('address must be of type Address')
        address.address_type = address_type
        if address_type is AddressType.Billing:
            self.billing_address = address
        else:
            self.shipping_address = address
        return self

    def with_alias(self, action, value):
        self.alias = value
        self.alias_action = action
        return self

    def with_cash_back(self, value):
        self.cash_back_amount = value
        self.transaction_modifier = TransactionModifier.CashBack
        return self

    def with_client_transaction_id(self, value):
        if (self.transaction_type is TransactionType.Reversal
                or self.transaction_type is TransactionType.Refund):
            if isinstance(self.payment_method, TransactionReference):
                self.payment_method.client_transaction_id = value
            else:
                self.payment_method = TransactionReference()
                self.payment_method.client_transaction_id = value
        else:
            self.client_transaction_id = value
        return self

    def with_commercial_request(self, value):
        self.level_2_request = value
        self.transaction_modifier = TransactionModifier.LevelII
        return self

    def with_hosted_payment_data(self, value):
        client = ServicesContainer.instance().get_client('default')
        if client.supports_hosted_payments:
            self.hosted_payment_data = value
            return self
        raise BuilderException(
            'Your current gateway does not support hosted payments.')

    def with_offline_auth_code(self, value):
        self.offline_auth_code = value
        self.transaction_modifier = TransactionModifier.Offline
        return self

    def with_one_time_payment(self, value):
        self.one_time_payment = value
        self.transaction_modifier = TransactionModifier.Recurring
        return self

    def with_payment_method(self, value):
        self.payment_method = value
        if isinstance(value, EBTCardData) and value.serial_number is not None:
            self.transaction_modifier = TransactionModifier.Voucher
        return self

    def with_recurring_info(self, recurring_type, recurring_sequence):
        self.recurring_type = recurring_type
        self.recurring_sequence = recurring_sequence
        return self

    def with_transaction_id(self, value):
        if isinstance(self.payment_method, TransactionReference):
            self.payment_method.transaction_id = value
        else:
            self.payment_method = TransactionReference()
            self.payment_method.transaction_id = value
        return self

    def __init__(self, transaction_type, payment_method=None):
        TransactionBuilder.__init__(self, transaction_type, payment_method)

    def execute(self, config_name=None):
        """
        Executes the authorization builder against the gateway.
        :return: Transaction
        """

        if config_name is None:
            config_name = "default"

        TransactionBuilder.execute(self)

        client = ServicesContainer.instance().get_client(config_name)
        return client.process_authorization(self)

    def serialize(self, config_name=None):
        """
        Serializes an authorization builder for hosted payment page requests.
        Requires the gateway and account support hosted payment pages.
        :return: string
        """

        if config_name is None:
            config_name = "default"

        self.transaction_modifier = TransactionModifier.HostedRequest
        TransactionBuilder.execute(self)

        client = ServicesContainer.instance().get_client(config_name)
        if client and client.supports_hosted_payments:
            return client.serialize_request(self)
        raise BuilderException(
            'Your current gateway does not support hosted payments.')

    def setup_validations(self):
        self.validations.of(TransactionType.Auth | TransactionType.Sale |
                            TransactionType.Refund | TransactionType.AddValue) \
            .check('amount').is_not_none() \
            .check('currency').is_not_none() \
            .check('payment_method').is_not_none()

        self.validations.of(TransactionType.Auth |
                            TransactionType.Sale |
                            TransactionType.Verify) \
            .with_constraint('transaction_modifier', TransactionModifier.HostedRequest) \
            .check('amount').is_not_none() \
            .check('currency').is_not_none()

        self.validations.of(TransactionType.Auth | TransactionType.Sale) \
            .with_constraint('transaction_modifier', TransactionModifier.Offline) \
            .check('amount').is_not_none() \
            .check('currency').is_not_none() \
            .check('offline_auth_code').is_not_none()

        self.validations.of(TransactionType.BenefitWithdrawal) \
            .with_constraint('transaction_modifier', TransactionModifier.CashBack) \
            .check('amount').is_not_none() \
            .check('currency').is_not_none() \
            .check('payment_method').is_not_none()

        self.validations.of(
            TransactionType.Balance).check('payment_method').is_not_none()

        self.validations.of(TransactionType.Alias) \
            .check('alias_action').is_not_none() \
            .check('alias').is_not_none()

        self.validations.of(
            TransactionType.Replace).check('replacement_card').is_not_none()

        self.validations.of(0) \
            .with_constraint('payment_method', PaymentMethodType.ACH) \
            .check('billing_address').is_not_none()


class ManagementBuilder(TransactionBuilder):
    """
    Used to follow up transactions for the supported
    payment method types.
    """

    amount = None
    auth_amount = None
    currency = None
    description = None
    gratuity = None
    po_number = None
    reason_code = None
    tax_amount = None
    tax_type = None

    @property
    def authorization_code(self):
        if isinstance(self.payment_method, TransactionReference):
            return self.payment_method.auth_code
        return None

    @property
    def client_transaction_id(self):
        if isinstance(self.payment_method, TransactionReference):
            return self.payment_method.client_transaction_id
        return None

    @property
    def order_id(self):
        if isinstance(self.payment_method, TransactionReference):
            return self.payment_method.order_id
        return None

    @property
    def transaction_id(self):
        if isinstance(self.payment_method, TransactionReference):
            return self.payment_method.transaction_id
        return None

    def with_po_number(self, value):
        self.transaction_modifier = TransactionModifier.LevelII
        self.po_number = value
        return self

    def with_tax_amount(self, value):
        self.transaction_modifier = TransactionModifier.LevelII
        self.tax_amount = value
        return self

    def with_tax_type(self, value):
        self.transaction_modifier = TransactionModifier.LevelII
        self.tax_type = value
        return self

    def __init__(self, transaction_type):
        TransactionBuilder.__init__(self, transaction_type)

    def execute(self, config_name=None):
        """
        Executes the builder against the gateway.
        :return: Transaction
        """

        if config_name is None:
            config_name = "default"

        TransactionBuilder.execute(self)

        client = ServicesContainer.instance().get_client(config_name)
        return client.manage_transaction(self)

    def setup_validations(self):
        self.validations.of(TransactionType.Capture | TransactionType.Edit |
                            TransactionType.Hold | TransactionType.Release) \
            .check('transaction_id').is_not_none()

        self.validations.of(TransactionType.Edit) \
            .with_constraint('transaction_modifier', TransactionModifier.LevelII) \
            .check('tax_type').is_not_none()

        self.validations.of(TransactionType.Refund) \
            .when('amount').is_not_none() \
            .check('currency').is_not_none()


class RecurringBuilder(TransactionBuilder):
    key = None
    order_id = None
    entity = None
    search_criteria = None

    def add_search_criteria(self, key, value):
        self.search_criteria[key] = value
        return self

    def __init__(self, transaction_type, entity=None):
        TransactionBuilder.__init__(self, transaction_type)
        self.entity = entity
        self.key = entity.key
        self.search_criteria = {}

    def execute(self, config_name=None):
        """
        Executes the builder against the gateway.
        :return: RecurringEntity
        """

        if config_name is None:
            config_name = "default"

        TransactionBuilder.execute(self)

        client = ServicesContainer.instance().get_recurring_client(config_name)
        return client.process_recurring(self)

    def setup_validations(self):
        self.validations.of(TransactionType.Edit | TransactionType.Delete | TransactionType.Fetch) \
            .check('key').is_not_none()

        self.validations.of(
            TransactionType.Search).check('search_criteria').is_not_none()


class ReportBuilder(BaseBuilder):
    report_type = None
    timezone_conversion = None

    def __init__(self, report_type):
        BaseBuilder.__init__(self)
        self.report_type = report_type

    def execute(self, config_name=None):
        """
        Executes the builder against the gateway.
        :return: Report
        """

        if config_name is None:
            config_name = "default"

        client = ServicesContainer.instance().get_client(config_name)
        return client.process_report(self)


class TransactionReportBuilder(ReportBuilder):
    device_id = None
    end_date = None
    start_date = None
    transaction_id = None

    def __init__(self, report_type):
        ReportBuilder.__init__(self, report_type)

    def setup_validations(self):
        self.validations.of(ReportType.TransactionDetail) \
            .check('transaction_id').is_not_none() \
            .check('device_id').is_none() \
            .check('end_date').is_none() \
            .check('start_date').is_none()

        self.validations.of(
            ReportType.Activity).check('transaction_id').is_none()
