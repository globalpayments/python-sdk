"""
"""

from dataclasses import dataclass, field
from typing import List
from typing import Optional, Dict, Any, Union, Self

import globalpayments as gp
from globalpayments.api.entities.address import Address
from globalpayments.api.entities.alternative_payment_response import (
    AlternativePaymentResponse,
)
from globalpayments.api.entities.batch_summary import BatchSummary
from globalpayments.api.entities.card import Card
from globalpayments.api.entities.card_issuer_response import CardIssuerResponse
from globalpayments.api.entities.dcc_rate_data import DccRateData
from globalpayments.api.entities.debit_mac import DebitMac
from globalpayments.api.entities.ecommerce_info import ECommerceInfo
from globalpayments.api.entities.encryption_data import EncryptionData
from globalpayments.api.entities.enums import (
    PaymentMethodType,
    TransactionType,
    SecCode,
    EntryMethod,
    PaymentEntryMode,
    PaymentSchedule,
)
from globalpayments.api.entities.exceptions import (
    ApiException,
    UnsupportedTransactionException,
)
from globalpayments.api.entities.payer_details import PayerDetails
from globalpayments.api.entities.three_d_secure import ThreeDSecure
from globalpayments.api.entities.transaction_summary import TransactionSummary
from globalpayments.api.payment_methods import GiftCard
from globalpayments.api.payment_methods import TransactionReference


@dataclass
class Transaction(object):
    """
    Transaction Response
    """

    authorized_amount: Optional[str] = field(default=None)
    available_balance: Optional[str] = field(default=None)
    avs_response_code: Optional[str] = field(default=None)
    avs_response_message: Optional[str] = field(default=None)
    balance_amount: Optional[str] = field(default=None)
    batch_summary: Optional["BatchSummary"] = field(default=None)
    card_type: Optional[str] = field(default=None)
    card_last_4: Optional[str] = field(
        default=None
    )  # Note: also referenced as card_last4 in code
    card_brand_transaction_id: Optional[str] = field(default=None)
    cavv_response_code: Optional[str] = field(default=None)
    commercial_indicator: Optional[str] = field(default=None)
    cvn_response_code: Optional[str] = field(default=None)
    cvn_response_message: Optional[str] = field(default=None)
    debit_mac: Optional["DebitMac"] = field(default=None)
    emv_issuer_response: Optional[str] = field(default=None)
    host_response_date: Optional[str] = field(default=None)
    points_balance_amount: Optional[str] = field(default=None)
    recurring_data_code: Optional[str] = field(default=None)
    reference_number: Optional[str] = field(default=None)
    response_code: Optional[str] = field(default=None)
    response_message: Optional[str] = field(default=None)
    response_values: Dict[str, str] = field(default_factory=dict)
    timestamp: Optional[str] = field(default=None)
    transaction_descriptor: Optional[str] = field(default=None)
    token: Optional[str] = field(default=None)
    gift_card: Optional["GiftCard"] = field(default=None)
    transaction_reference: Optional[TransactionReference] = field(default=None)
    three_d_secure: Optional[ThreeDSecure] = field(default=None)
    # Additional attributes needed for GpApiMapping
    multi_capture: Optional[bool] = field(default=None)
    fingerprint: Optional[str] = field(default=None)
    fingerprint_indicator: Optional[str] = field(default=None)
    token_usage_mode: Optional[str] = field(default=None)
    card_details: Optional["Card"] = field(default=None)
    dcc_rate_data: Optional["DccRateData"] = field(default=None)
    card_last4: Optional[str] = field(default=None)
    avs_address_response: Optional[str] = field(default=None)
    card_issuer_response: Optional["CardIssuerResponse"] = field(default=None)
    account_number_last4: Optional[str] = field(default=None)
    account_type: Optional[str] = field(default=None)
    payer_details: Optional["PayerDetails"] = field(default=None)
    alternative_payment_response: Optional["AlternativePaymentResponse"] = field(
        default=None
    )

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
    def from_id(
        transaction_id, payment_method_type=PaymentMethodType.Credit, order_id=None
    ):
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
        from globalpayments.api.builders import ManagementBuilder

        builder = ManagementBuilder(TransactionType.Auth)
        builder.with_payment_method(self.transaction_reference)
        if amount is not None:
            builder.with_amount(amount)
        return builder

    def capture(self, amount=None):
        """
        Captures the original transaction.
        :param amount: The amount to capture
        :return: ManagementBuilder
        """
        from globalpayments.api.builders import ManagementBuilder

        builder = ManagementBuilder(TransactionType.Capture)
        builder.with_payment_method(self.transaction_reference)
        if amount is not None:
            builder.with_amount(amount)
        return builder

    def edit(self):
        """
        Edits the original transaction.
        :return: ManagementBuilder
        """
        from globalpayments.api.builders import ManagementBuilder

        return ManagementBuilder(TransactionType.Edit).with_payment_method(
            self.transaction_reference
        )

    def hold(self):
        """
        Places the original transaction on hold.
        :return: ManagementBuilder
        """
        from globalpayments.api.builders import ManagementBuilder

        return ManagementBuilder(TransactionType.Hold).with_payment_method(
            self.transaction_reference
        )

    def refund(self, amount=None):
        """
        Refunds/returns the original transaction.
        :param amount:The amount to refund/return
        :return: ManagementBuilder
        """
        from globalpayments.api.builders import ManagementBuilder

        builder = ManagementBuilder(TransactionType.Refund)
        builder.with_payment_method(self.transaction_reference)
        if amount is not None:
            builder.with_amount(amount)
        return builder

    def release(self):
        """
        Releases the original transaction from a hold.
        :return: ManagementBuilder
        """
        from globalpayments.api.builders import ManagementBuilder

        return ManagementBuilder(TransactionType.Release).with_payment_method(
            self.transaction_reference
        )

    def reverse(self, amount=None):
        """
        Reverses the original transaction.
        :param amount: The original authorization amount
        :return: ManagementBuilder
        """
        from globalpayments.api.builders import ManagementBuilder

        builder = ManagementBuilder(TransactionType.Reversal)
        builder.with_payment_method(self.transaction_reference)
        if amount is not None:
            builder.with_amount(amount)
        return builder

    def void(self):
        """
        Voids the original transaction.
        :return: ManagementBuilder
        """
        from globalpayments.api.builders import ManagementBuilder

        return ManagementBuilder(TransactionType.Void).with_payment_method(
            self.transaction_reference
        )


@dataclass
class RecurringEntity(object):
    """
    Base implementation for recurring resource types.
    """

    id: Optional[str] = field(default=None)
    key: Optional[str] = field(default=None)

    def create(self, config_name: str = "default") -> Optional["RecurringEntity"]:
        """
        Creates a resource
        :return: RecurringEntity or None if creation fails
        """

        result = gp.api.services.RecurringService.create(self, config_name)
        if isinstance(result, RecurringEntity):
            return result
        return None

    def delete(self, force: bool = False, config_name: str = "default") -> Any:
        """
        Delete a record from the gateway.
        :param force: Indicates if the deletion should be forced
        :return: void
        """
        try:
            return gp.api.services.RecurringService.delete(self, force, config_name)
        except ApiException as exc:
            raise ApiException(
                "Failed to delete record, see inner exception for more details. ", exc
            )

    @staticmethod
    def find(
        identifier_name: str = "", identifier: str = "", config_name: str = "default"
    ) -> Optional["RecurringEntity"]:
        """
        Searches for a specific record by `id`.
        :param identifier_name: The name of the identifier
        :param identifier: The ID of the record to find
        :param config_name: The configuration name to use
        :return: RecurringEntity or None if not found
        """
        client = gp.api.ServicesContainer.instance().get_recurring_client(config_name)
        if client is not None and client.supports_retrieval:
            response = (
                gp.api.services.RecurringService.search()
                .add_search_criteria(identifier_name, identifier)
                .execute(config_name)
            )
            entity = response[0] if response is not None and len(response) > 0 else None
            if entity is not None:
                return gp.api.services.RecurringService.get(entity, config_name)
            return None
        raise UnsupportedTransactionException()

    @staticmethod
    def find_all(entity: Any, config_name: str = "default") -> List[Any]:
        """
        Lists all records of base type
        :param entity: The entity to search for
        :param config_name: The configuration name to use
        :return: List of found entities
        """
        client = gp.api.ServicesContainer.instance().get_recurring_client(config_name)
        if client is not None and client.supports_retrieval:
            return (
                gp.api.services.RecurringService.search(entity).execute(config_name)
                or []
            )
        raise UnsupportedTransactionException()

    def save_changes(self, config_name: str = "default") -> Any:
        try:
            return gp.api.services.RecurringService.edit(self, config_name)
        except ApiException as exc:
            raise ApiException(
                "Update failed, see inner exception for more details. " + exc.message,
                exc,
            )


@dataclass
class Customer(RecurringEntity):
    """
    A customer resource.
    Mostly used in recurring scenarios.
    """

    title: Optional[str] = field(default=None)
    first_name: Optional[str] = field(default=None)
    last_name: Optional[str] = field(default=None)
    company: Optional[str] = field(default=None)
    address: Optional["Address"] = field(default=None)
    home_phone: Optional[str] = field(default=None)
    work_phone: Optional[str] = field(default=None)
    fax: Optional[str] = field(default=None)
    mobile_phone: Optional[str] = field(default=None)
    email: Optional[str] = field(default=None)
    comments: Optional[str] = field(default=None)
    department: Optional[str] = field(default=None)
    status: Optional[str] = field(default=None)
    device_fingerprint: Optional[str] = field(default=None)
    payment_methods: Optional[List["RecurringPaymentMethod"]] = field(default=None)

    def add_payment_method(
        self, payment_id: str, payment_method: Any
    ) -> "RecurringPaymentMethod":
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
    def find(
        identifier_name: str = "customerIdentifier",
        identifier: str = "",
        config_name: str = "default",
    ) -> Optional["Customer"]:
        if identifier_name != "customerIdentifier" and not identifier:
            identifier = identifier_name
            identifier_name = "customerIdentifier"

        result = RecurringEntity.find(identifier_name, identifier, config_name)
        if result is not None and isinstance(result, Customer):
            return result
        return None

    @staticmethod
    def find_all(entity: Any = None, config_name: str = "default") -> List["Customer"]:
        if entity is None or isinstance(entity, str):
            if isinstance(entity, str):
                config_name = entity
            entity = Customer()
        return RecurringEntity.find_all(entity, config_name)


@dataclass
class RecurringPaymentMethod(RecurringEntity):
    address: Optional["Address"] = field(default=None)
    commercial_indicator: Optional[str] = field(default=None)
    customer_key: Optional[str] = field(default=None)
    expiration_date: Optional[str] = field(default=None)
    name_on_account: Optional[str] = field(default=None)
    payment_method: Optional[Any] = field(default=None)
    payment_method_type: PaymentMethodType = field(default=PaymentMethodType.Recurring)
    payment_type: Optional[str] = field(default=None)
    preferred_payment: Optional[bool] = field(default=None)
    status: Optional[str] = field(default=None)
    tax_type: Optional[str] = field(default=None)
    sec_code: Optional[SecCode] = field(default=None)

    # Card related attributes
    is_card_data: bool = field(default=False)
    is_track_data: bool = field(default=False)
    tokenizable: bool = field(default=False)
    reader_present: bool = field(default=False)
    card_present: bool = field(default=False)
    number: Optional[str] = field(default=None)
    exp_month: Optional[int] = field(default=None)
    exp_year: Optional[int] = field(default=None)
    cvn: Optional[str] = field(default=None)
    value: Optional[str] = field(default=None)  # For track data
    entry_method: Optional[EntryMethod] = field(default=None)

    # Check related attributes
    check_holder_name: Optional[str] = field(default=None)
    check_name: Optional[str] = field(default=None)
    phone_number: Optional[str] = field(default=None)
    drivers_license_number: Optional[str] = field(default=None)
    drivers_license_state: Optional[str] = field(default=None)
    ssn_last_4: Optional[str] = field(default=None)
    birth_year: Optional[str] = field(default=None)

    # Security related
    pin_block: Optional[str] = field(default=None)
    encryption_data: Optional["EncryptionData"] = field(default=None)

    def __init__(
        self,
        payment_method_or_customer: Optional[Union[str, Any]] = None,
        payment_id: Optional[str] = None,
    ):
        if isinstance(payment_method_or_customer, str):
            self.customer_key = payment_method_or_customer
            self.key = payment_id
            self.payment_type = "Credit Card"
        else:
            self.payment_method = payment_method_or_customer

    def authorize(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Auth, self)
        if amount is not None:
            builder.with_amount(amount)
        builder.with_one_time_payment(True)
        return builder

    def charge(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Sale, self)
        if amount is not None:
            builder.with_amount(amount)
        builder.with_one_time_payment(True)
        return builder

    def refund(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Refund, self)
        if amount is not None:
            builder.with_amount(amount)
        return builder

    def verify(self) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        return AuthorizationBuilder(TransactionType.Verify, self)

    def add_schedule(self, schedule_id: str) -> "Schedule":
        data = Schedule()
        data.customer_key = self.customer_key
        data.payment_key = self.key
        data.id = schedule_id
        return data

    @staticmethod
    def find(
        identifier_name: str = "paymentMethodIdentifier",
        identifier: str = "",
        config_name: str = "default",
    ) -> Optional["RecurringPaymentMethod"]:
        if identifier_name != "paymentMethodIdentifier" and not identifier:
            identifier = identifier_name
            identifier_name = "paymentMethodIdentifier"

        result = RecurringEntity.find(identifier_name, identifier, config_name)
        if result is not None and isinstance(result, RecurringPaymentMethod):
            return result
        return None

    @staticmethod
    def find_all(
        entity: Any = None, config_name: str = "default"
    ) -> List["RecurringPaymentMethod"]:
        if entity is None or isinstance(entity, str):
            if isinstance(entity, str):
                config_name = entity
            entity = RecurringPaymentMethod()
        return RecurringEntity.find_all(entity, config_name)


@dataclass
class Schedule(RecurringEntity):
    amount: Optional[Union[int, float]] = field(default=None)
    cancellation_date: Optional[str] = field(default=None)
    currency: Optional[str] = field(default=None)
    customer_key: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    device_id: Optional[str] = field(default=None)
    email_notification: Optional[bool] = field(default=None)
    email_receipt: Optional[bool] = field(default=None)
    end_date: Optional[str] = field(default=None)
    frequency: Optional[str] = field(default=None)
    has_started: Optional[bool] = field(default=False)
    invoice_number: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    next_processing_date: Optional[str] = field(default=None)
    number_of_payments: Optional[int] = field(default=None)
    po_number: Optional[str] = field(default=None)
    payment_key: Optional[str] = field(default=None)
    payment_schedule: Optional["PaymentSchedule"] = field(default=None)
    reprocessing_count: Optional[int] = field(default=None)
    start_date: Optional[str] = field(default=None)
    status: Optional[str] = field(default=None)
    tax_amount: Optional[Union[int, float]] = field(default=None)

    @property
    def total_amount(self):
        amount = self.amount or 0
        tax_amount = self.tax_amount or 0
        return amount + tax_amount

    def with_status(self, value) -> Self:
        self.status = value
        return self

    def with_amount(self, value) -> Self:
        self.amount = int(value * 100)
        return self

    def with_reprocessing_count(self, value) -> Self:
        self.reprocessing_count = value
        return self

    def with_start_date(self, value) -> Self:
        self.start_date = value
        return self

    def with_end_date(self, value) -> Self:
        self.end_date = value
        return self

    def with_frequency(self, value) -> Self:
        self.frequency = value
        return self

    def with_currency(self, value) -> Self:
        self.currency = value
        return self

    def with_email_receipt(self, value) -> Self:
        self.email_receipt = value
        return self

    def __init__(self, customer_key=None, payment_key=None):
        self.customer_key = customer_key
        self.payment_key = payment_key

    @staticmethod
    def find(
        identifier_name: str = "scheduleIdentifier",
        identifier: str = "",
        config_name: str = "default",
    ) -> Optional["Schedule"]:
        if identifier_name != "scheduleIdentifier" and not identifier:
            identifier = identifier_name
            identifier_name = "scheduleIdentifier"

        result = RecurringEntity.find(identifier_name, identifier, config_name)
        if result is not None and isinstance(result, Schedule):
            return result
        return None

    @staticmethod
    def find_all(entity: Any = None, config_name: str = "default") -> List["Schedule"]:
        if entity is None or isinstance(entity, str):
            if isinstance(entity, str):
                config_name = entity
            entity = Schedule()
        return RecurringEntity.find_all(entity, config_name)
