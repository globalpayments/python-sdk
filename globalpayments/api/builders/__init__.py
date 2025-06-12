"""
Builder classes for payment API requests
"""

import dataclasses
from typing import Dict, Optional, Any, TYPE_CHECKING, Union, Self, List

# Import ServicesContainer inside functions to avoid circular imports
from globalpayments.api.builders.validations import Validations
from globalpayments.api.entities import (
    Address,
    TransactionReference,
    Customer,
)
from globalpayments.api.entities.dispute_document import DisputeDocument
from globalpayments.api.entities.enums import (
    AddressType,
    EmvChipCondition,
    InquiryType,
    PaymentMethodType,
    RecurringSequence,
    RecurringType,
    ReportType,
    TransactionModifier,
    TransactionType,
    StoredCredentialInitiator,
    AliasAction,
    PaymentMethodUsageMode,
    SortDirection,
    SearchCriteria,
)
from globalpayments.api.entities.exceptions import BuilderException
from globalpayments.api.entities.reporting import SearchCriteriaBuilder
from globalpayments.api.entities.stored_credentials import StoredCredential
from globalpayments.api.payment_methods import EBTCardData

if TYPE_CHECKING:
    from globalpayments.api.entities.ecommerce_info import ECommerceInfo
    from globalpayments.api.entities.hosted_payment_data import HostedPaymentData
    from globalpayments.api.payment_methods import GiftCard


class BaseBuilder(object):
    validations: Optional[Validations] = None

    def __init__(self) -> None:
        self.validations = Validations()
        self.setup_validations()

    def execute(self, config_name: Optional[str] = None) -> Optional[Any]:
        if self.validations is not None:
            self.validations.validate(self)
        return None

    def setup_validations(self) -> None:
        pass

    def set_property_if_exists(self, *args: Any) -> None:
        if hasattr(self, args[0]):
            setattr(self, args[0], args[1])
        else:
            raise BuilderException("Unknown property {}".format(args[0]))


@dataclasses.dataclass
class TransactionBuilder(BaseBuilder):
    transaction_type: Optional[TransactionType] = None
    transaction_modifier: Optional[TransactionModifier] = None
    payment_method: Any = (
        None  # This is a generic payment method that could be any type
    )

    def __init__(
        self, transaction_type: TransactionType, payment_method: Any = None
    ) -> None:
        BaseBuilder.__init__(self)
        self.transaction_type = transaction_type
        self.payment_method = payment_method

    def with_transaction_type(self, transaction_type: TransactionType) -> Self:
        self.transaction_type = transaction_type
        return self

    def with_transaction_modifier(
        self, transaction_modifier: TransactionModifier
    ) -> Self:
        self.transaction_modifier = transaction_modifier
        return self

    def with_payment_method(self, value: Any) -> Self:
        self.payment_method = value
        return self


@dataclasses.dataclass
class AuthorizationBuilder(TransactionBuilder):
    """
    Used to create charges, verifies, etc. for the supported
    payment method types.
    """

    account_type: Optional[str] = None
    alias: Optional[str] = None
    alias_action: Optional[AliasAction] = None  # Enum type
    allow_duplicates: Optional[bool] = None
    allow_partial_auth: Optional[bool] = None
    amount: Optional[float] = None
    auth_amount: Optional[float] = None
    balance_inquiry_type: Optional[InquiryType] = None
    billing_address: Optional[Address] = None
    cash_back_amount: Optional[float] = None
    chip_condition: Optional[EmvChipCondition] = None
    client_transaction_id: Optional[str] = None
    currency: Optional[str] = None
    customer_data: Optional[Customer] = None
    customer_id: Optional[str] = None
    customer_ip_address: Optional[str] = None
    cvn: Optional[str] = None
    description: Optional[str] = None
    dynamic_descriptor: Optional[str] = None
    ecommerce_info: Optional["ECommerceInfo"] = None
    gratuity: Optional[float] = None
    convenience_amt: Optional[float] = None
    shipping_amt: Optional[float] = None
    hosted_payment_data: Optional["HostedPaymentData"] = None
    idempotency_key: Optional[str] = None
    invoice_number: Optional[str] = None
    level_2_request: Optional[bool] = None
    message_authentication_code: Optional[str] = None
    multi_capture: Optional[bool] = None
    offline_auth_code: Optional[str] = None
    one_time_payment: bool = False
    order_id: Optional[str] = None
    payment_method_usage_mode: Optional[PaymentMethodUsageMode] = None
    pos_sequence_number: Optional[str] = None
    product_id: Optional[str] = None
    recurring_sequence: Optional[RecurringSequence] = None
    recurring_type: Optional[RecurringType] = None
    request_multi_use_token: bool = False
    replacement_card: Optional["GiftCard"] = None
    schedule_id: Optional[str] = None
    shipping_address: Optional[Address] = None
    stored_credential: Optional[StoredCredential] = None
    tag_data: Optional[str] = None
    timestamp: Optional[str] = None
    transaction_initiator: Optional[StoredCredentialInitiator] = None
    card_brand_transaction_id: Optional[str] = None

    def with_address(
        self, address: Address, address_type: AddressType = AddressType.Billing
    ) -> Self:
        if not isinstance(address, Address):
            raise BuilderException("address must be of type Address")
        address.address_type = address_type
        if address_type is AddressType.Billing:
            self.billing_address = address
        else:
            self.shipping_address = address
        return self

    def with_invoice_number(self, invoice_number: str) -> Self:
        self.invoice_number = invoice_number
        return self

    def with_idempotency_key(self, idempotency_key: str) -> Self:
        self.idempotency_key = idempotency_key
        return self

    def with_alias(self, action: AliasAction, value: str) -> Self:
        self.alias = value
        self.alias_action = action
        return self

    def with_cash_back(self, value: float) -> Self:
        self.cash_back_amount = value
        self.transaction_modifier = TransactionModifier.CashBack
        return self

    def with_client_transaction_id(self, value: str) -> Self:
        if (
            self.transaction_type is TransactionType.Reversal
            or self.transaction_type is TransactionType.Refund
        ):
            if isinstance(self.payment_method, TransactionReference):
                self.payment_method.client_transaction_id = value
            else:
                self.payment_method = TransactionReference()
                self.payment_method.client_transaction_id = value
        else:
            self.client_transaction_id = value
        return self

    def with_card_brand_storage(
        self,
        transaction_initiator: StoredCredentialInitiator,
        value: Optional[str] = None,
    ) -> Self:
        self.transaction_initiator = transaction_initiator
        if value is not None:
            self.card_brand_transaction_id = value
        return self

    def with_commercial_request(self, value: bool) -> Self:
        self.level_2_request = value
        self.transaction_modifier = TransactionModifier.LevelII
        return self

    def with_hosted_payment_data(self, value: "HostedPaymentData") -> Self:
        from globalpayments.api import ServicesContainer

        client = ServicesContainer.instance().get_client("default")
        if (
            client is not None
            and hasattr(client, "supports_hosted_payments")
            and client.supports_hosted_payments
        ):
            self.hosted_payment_data = value
            return self
        raise BuilderException("Your current gateway does not support hosted payments.")

    def with_offline_auth_code(self, value: str) -> Self:
        self.offline_auth_code = value
        self.transaction_modifier = TransactionModifier.Offline
        return self

    def with_one_time_payment(self, value: bool) -> Self:
        self.one_time_payment = value
        self.transaction_modifier = TransactionModifier.Recurring
        return self

    def with_payment_method(self, value: Any) -> Self:
        self.payment_method = value
        if isinstance(value, EBTCardData) and value.serial_number is not None:
            self.transaction_modifier = TransactionModifier.Voucher
        return self

    def with_recurring_info(
        self, recurring_type: RecurringType, recurring_sequence: RecurringSequence
    ) -> Self:
        self.recurring_type = recurring_type
        self.recurring_sequence = recurring_sequence
        return self

    def with_transaction_id(self, value: str) -> Self:
        if isinstance(self.payment_method, TransactionReference):
            self.payment_method.transaction_id = value
        else:
            self.payment_method = TransactionReference()
            self.payment_method.transaction_id = value
        return self

    def with_tag_data(self, value: str) -> Self:
        self.tag_data = value
        return self

    def with_account_type(self, account_type: str) -> Self:
        self.account_type = account_type
        return self

    def with_allow_duplicates(self, allow_duplicates: bool) -> Self:
        self.allow_duplicates = allow_duplicates
        return self

    def with_allow_partial_auth(self, allow_partial_auth: bool) -> Self:
        self.allow_partial_auth = allow_partial_auth
        return self

    def with_amount(self, raw_amount: Optional[Union[float, int, str]]) -> Self:
        if raw_amount is None:
            self.amount = None
            return self
        try:
            amount = float(raw_amount)
            self.amount = amount
        except ValueError:
            pass
        return self

    def with_auth_amount(self, auth_amount: float) -> Self:
        self.auth_amount = auth_amount
        return self

    def with_balance_inquiry_type(self, balance_inquiry_type: InquiryType) -> Self:
        self.balance_inquiry_type = balance_inquiry_type
        return self

    def with_chip_condition(self, chip_condition: EmvChipCondition) -> Self:
        self.chip_condition = chip_condition
        return self

    def with_currency(self, currency: str) -> Self:
        self.currency = currency
        return self

    def with_customer_data(self, customer: Customer) -> Self:
        self.customer_data = customer
        return self

    def with_customer_id(self, customer_id: str) -> Self:
        self.customer_id = customer_id
        return self

    def with_customer_ip_address(self, customer_ip_address: str) -> Self:
        self.customer_ip_address = customer_ip_address
        return self

    def with_cvn(self, cvn: str) -> Self:
        self.cvn = cvn
        return self

    def with_description(self, description: str) -> Self:
        self.description = description
        return self

    def with_dynamic_descriptor(self, dynamic_descriptor: str) -> Self:
        self.dynamic_descriptor = dynamic_descriptor
        return self

    def with_ecommerce_info(self, ecommerce_info: "ECommerceInfo") -> Self:
        self.ecommerce_info = ecommerce_info
        return self

    def with_gratuity(self, gratuity: float) -> Self:
        self.gratuity = gratuity
        return self

    def with_convenience_amt(self, convenience_amt: float) -> Self:
        self.convenience_amt = convenience_amt
        return self

    def with_shipping_amt(self, shipping_amt: float) -> Self:
        self.shipping_amt = shipping_amt
        return self

    def with_stored_credential(self, stored_credential: "StoredCredential") -> Self:
        self.stored_credential = stored_credential
        return self

    def with_level_2_request(self, level_2_request: bool) -> Self:
        self.level_2_request = level_2_request
        return self

    def with_message_authentication_code(
        self, message_authentication_code: str
    ) -> Self:
        self.message_authentication_code = message_authentication_code
        return self

    def with_multi_capture(self, multi_capture: bool) -> Self:
        self.multi_capture = multi_capture
        return self

    def with_order_id(self, order_id: str) -> Self:
        self.order_id = order_id
        return self

    def with_payment_method_usage_mode(
        self, payment_method_usage_mode: PaymentMethodUsageMode
    ) -> Self:
        self.payment_method_usage_mode = payment_method_usage_mode
        return self

    def with_pos_sequence_number(self, pos_sequence_number: str) -> Self:
        self.pos_sequence_number = pos_sequence_number
        return self

    def with_product_id(self, product_id: str) -> Self:
        self.product_id = product_id
        return self

    def with_request_multi_use_token(self, request_multi_use_token: bool) -> Self:
        self.request_multi_use_token = request_multi_use_token
        return self

    def with_replacement_card(self, replacement_card: "GiftCard") -> Self:
        self.replacement_card = replacement_card
        return self

    def with_schedule_id(self, schedule_id: str) -> Self:
        self.schedule_id = schedule_id
        return self

    def with_timestamp(self, timestamp: str) -> Self:
        self.timestamp = timestamp
        return self

    def __init__(
        self, transaction_type: TransactionType, payment_method: Any = None
    ) -> None:
        TransactionBuilder.__init__(self, transaction_type, payment_method)

    def execute(self, config_name: Optional[str] = None) -> Any:
        """
        Executes the authorization builder against the gateway.
        :return: Transaction
        """

        if config_name is None:
            config_name = "default"

        TransactionBuilder.execute(self)

        from globalpayments.api import ServicesContainer

        client = ServicesContainer.instance().get_client(config_name)
        if client is not None:
            return client.process_authorization(self)
        return None

    def serialize(self, config_name: Optional[str] = None) -> str:
        """
        Serializes an authorization builder for hosted payment page requests.
        Requires the gateway and account support hosted payment pages.
        :return: string
        """

        if config_name is None:
            config_name = "default"

        self.transaction_modifier = TransactionModifier.HostedRequest
        TransactionBuilder.execute(self)

        from globalpayments.api import ServicesContainer

        client = ServicesContainer.instance().get_client(config_name)
        if (
            client is not None
            and hasattr(client, "supports_hosted_payments")
            and client.supports_hosted_payments is not None
            and client.supports_hosted_payments
        ):
            return client.serialize_request(self)
        raise BuilderException("Your current gateway does not support hosted payments.")

    def setup_validations(self):
        self.validations.of(
            TransactionType.Auth
            | TransactionType.Sale
            | TransactionType.Refund
            | TransactionType.AddValue
        ).check("amount").is_not_none().check("currency").is_not_none().check(
            "payment_method"
        ).is_not_none()

        self.validations.of(
            TransactionType.Auth | TransactionType.Sale | TransactionType.Verify
        ).with_constraint(
            "transaction_modifier", TransactionModifier.HostedRequest
        ).check(
            "amount"
        ).is_not_none().check(
            "currency"
        ).is_not_none()

        self.validations.of(
            TransactionType.Auth | TransactionType.Sale
        ).with_constraint("transaction_modifier", TransactionModifier.Offline).check(
            "amount"
        ).is_not_none().check(
            "currency"
        ).is_not_none().check(
            "offline_auth_code"
        ).is_not_none()

        self.validations.of(TransactionType.BenefitWithdrawal).with_constraint(
            "transaction_modifier", TransactionModifier.CashBack
        ).check("amount").is_not_none().check("currency").is_not_none().check(
            "payment_method"
        ).is_not_none()

        self.validations.of(TransactionType.Balance).check(
            "payment_method"
        ).is_not_none()

        self.validations.of(TransactionType.Alias).check(
            "alias_action"
        ).is_not_none().check("alias").is_not_none()

        self.validations.of(TransactionType.Replace).check(
            "replacement_card"
        ).is_not_none()

        self.validations.of(0).with_constraint(
            "payment_method", PaymentMethodType.ACH
        ).check("billing_address").is_not_none()


@dataclasses.dataclass
class ManagementBuilder(TransactionBuilder):
    """
    Used to follow up transactions for the supported
    payment method types.
    """

    amount: Optional[float] = None
    auth_amount: Optional[float] = None
    allow_duplicates: Optional[bool] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    gratuity: Optional[float] = None
    idempotency_key: Optional[str] = None
    payment_method_usage_mode: Optional[PaymentMethodUsageMode] = None
    po_number: Optional[str] = None
    reason_code: Optional[str] = None
    tax_amount: Optional[float] = None
    dispute_id: Optional[str] = None
    dispute_documents: Optional[List[DisputeDocument]] = None
    tax_type: Optional[str] = None

    @property
    def authorization_code(self) -> Optional[str]:
        if isinstance(self.payment_method, TransactionReference):
            return self.payment_method.auth_code
        return None

    @property
    def client_transaction_id(self) -> Optional[str]:
        if isinstance(self.payment_method, TransactionReference):
            return self.payment_method.client_transaction_id
        return None

    @property
    def order_id(self) -> Optional[str]:
        if isinstance(self.payment_method, TransactionReference):
            return self.payment_method.order_id
        return None

    @property
    def transaction_id(self) -> Optional[str]:
        if isinstance(self.payment_method, TransactionReference):
            return self.payment_method.transaction_id
        return None

    def with_idempotency_key(self, idempotency_key: str) -> Self:
        self.idempotency_key = idempotency_key
        return self

    def with_dispute_id(self, dispute_id: str) -> Self:
        self.dispute_id = dispute_id
        return self

    def with_dispute_documents(self, dispute_documents: List[DisputeDocument]) -> Self:
        self.dispute_documents = dispute_documents
        return self

    def with_payment_method_usage_mode(
        self, payment_method_usage_mode: PaymentMethodUsageMode
    ) -> Self:
        self.payment_method_usage_mode = payment_method_usage_mode
        return self

    def with_po_number(self, value: str) -> Self:
        self.transaction_modifier = TransactionModifier.LevelII
        self.po_number = value
        return self

    def with_tax_amount(self, value: float) -> Self:
        self.transaction_modifier = TransactionModifier.LevelII
        self.tax_amount = value
        return self

    def with_tax_type(self, value: str) -> Self:
        self.transaction_modifier = TransactionModifier.LevelII
        self.tax_type = value
        return self

    def with_allow_duplicates(self, allow_duplicates: bool) -> Self:
        self.allow_duplicates = allow_duplicates
        return self

    def with_amount(self, amount: float) -> Self:
        self.amount = amount
        return self

    def with_auth_amount(self, auth_amount: float) -> Self:
        self.auth_amount = auth_amount
        return self

    def with_currency(self, currency: str) -> Self:
        self.currency = currency
        return self

    def with_description(self, description: str) -> Self:
        self.description = description
        return self

    def with_gratuity(self, gratuity: float) -> Self:
        self.gratuity = gratuity
        return self

    def with_reason_code(self, reason_code: str) -> Self:
        self.reason_code = reason_code
        return self

    def __init__(
        self, transaction_type: TransactionType, payment_method: Any = None
    ) -> None:
        TransactionBuilder.__init__(self, transaction_type, payment_method)

    def execute(self, config_name: Optional[str] = None) -> Any:
        """
        Executes the builder against the gateway.
        :return: Transaction
        """

        if config_name is None:
            config_name = "default"

        TransactionBuilder.execute(self)

        from globalpayments.api import ServicesContainer

        client = ServicesContainer.instance().get_client(config_name)
        if client is not None:
            return client.manage_transaction(self)
        return None

    def setup_validations(self):
        self.validations.of(
            TransactionType.Capture
            | TransactionType.Edit
            | TransactionType.Hold
            | TransactionType.Release
        ).check("transaction_id").is_not_none()

        self.validations.of(TransactionType.Edit).with_constraint(
            "transaction_modifier", TransactionModifier.LevelII
        ).check("tax_type").is_not_none()

        self.validations.of(TransactionType.Refund).when("amount").is_not_none().check(
            "currency"
        ).is_not_none()


@dataclasses.dataclass
class RecurringBuilder(TransactionBuilder):
    key: Optional[str] = None
    order_id: Optional[str] = None
    entity: Any = None  # RecurringEntity
    search_criteria: Optional[Dict[str, Any]] = None
    force: bool = False

    def add_search_criteria(self, key: str, value: Any) -> Self:
        if self.search_criteria is not None:
            self.search_criteria[key] = value
        return self

    def with_key(self, key: str) -> Self:
        self.key = key
        return self

    def with_order_id(self, order_id: str) -> Self:
        self.order_id = order_id
        return self

    def with_entity(self, entity: Any) -> Self:
        self.entity = entity
        return self

    def with_force(self, force: bool) -> Self:
        self.force = force
        return self

    def __init__(self, transaction_type: TransactionType, entity: Any = None) -> None:
        TransactionBuilder.__init__(self, transaction_type)
        self.entity = entity
        if entity is not None:
            self.key = entity.key
        self.search_criteria = {}

    def execute(self, config_name: Optional[str] = None) -> Any:
        """
        Executes the builder against the gateway.
        :return: RecurringEntity
        """

        if config_name is None:
            config_name = "default"

        TransactionBuilder.execute(self)

        from globalpayments.api import ServicesContainer

        client = ServicesContainer.instance().get_recurring_client(config_name)
        if client is not None:
            return client.process_recurring(self)
        return None

    def setup_validations(self):
        self.validations.of(
            TransactionType.Edit | TransactionType.Delete | TransactionType.Fetch
        ).check("key").is_not_none()

        self.validations.of(TransactionType.Search).check(
            "search_criteria"
        ).is_not_none()


@dataclasses.dataclass
class ReportBuilder(BaseBuilder):
    report_type: Optional[ReportType] = None
    timezone_conversion: Any = None
    search_criteria: Dict[str, Any] = dataclasses.field(default_factory=dict)
    page: Optional[int] = None
    page_size: Optional[int] = None

    def add_search_criteria(self, key: str, value: Any) -> Self:
        if self.search_criteria is not None:
            self.search_criteria[key] = value
        return self

    def with_report_type(self, report_type: ReportType) -> Self:
        self.report_type = report_type
        return self

    def with_paging(self, page: int, page_size: int):
        self.page = page
        self.page_size = page_size

        return self

    def with_timezone_conversion(self, timezone_conversion: Any) -> Self:
        self.timezone_conversion = timezone_conversion
        return self

    def __init__(self, report_type: ReportType) -> None:
        BaseBuilder.__init__(self)
        self.report_type = report_type

    def execute(self, config_name: Optional[str] = None) -> Any:
        """
        Executes the builder against the gateway.
        :return: Report
        """

        if config_name is None:
            config_name = "default"

        from globalpayments.api import ServicesContainer

        client = ServicesContainer.instance().get_client(config_name)
        if client is not None:
            return client.process_report(self)
        return None


class MerchantInsightBuilder(BaseBuilder):
    """
    Placeholder for MerchantInsightBuilder functionality.
    Used for building merchant insight collector requests.
    """

    def __init__(self) -> None:
        BaseBuilder.__init__(self)

    def execute(self, config_name: Optional[str] = None) -> Any:
        """
        Executes the builder against the gateway.
        :return: Response from the gateway
        """
        if config_name is None:
            config_name = "default"

        # Here we would call get_client on ServicesContainer and execute the request
        # For now, just returning None to avoid type errors
        return None


@dataclasses.dataclass
class TransactionReportBuilder(ReportBuilder):
    device_id: Optional[str] = None
    end_date: Any = None  # datetime
    start_date: Any = None  # datetime
    transaction_id: Optional[str] = None
    search_criteria: Optional[Dict[str, Any]] = None
    deposit_order_by: Optional[Any] = None  # DepositSortProperty
    dispute_order_by: Optional[Any] = None  # DisputeSortProperty
    search_builder: Optional[SearchCriteriaBuilder] = None
    stored_payment_method_order_by: Optional[Any] = None
    transaction_order_by: Optional[Any] = None
    order: Optional[SortDirection] = None

    def __init__(self, report_type: ReportType) -> None:
        ReportBuilder.__init__(self, report_type)
        self.search_builder = SearchCriteriaBuilder(self)

    def with_device_id(self, device_id: Optional[str] = None) -> Self:
        if device_id is not None:
            self.device_id = device_id
        return self

    def with_dispute_id(self, dispute_id: Optional[str] = None) -> Self:
        self.search_builder.dispute_id = dispute_id
        return self

    def with_end_date(self, end_date: Any = None) -> Self:
        if end_date is not None:
            self.end_date = end_date
        return self

    def with_start_date(self, start_date: Any = None) -> Self:
        if start_date is not None:
            self.start_date = start_date
        return self

    def with_stored_payment_method_id(
        self, stored_payment_method_id: Optional[str] = None
    ) -> Self:
        if stored_payment_method_id is not None:
            self.search_builder.stored_payment_method_id = stored_payment_method_id
        return self

    def with_transaction_id(self, transaction_id: Optional[str] = None) -> Self:
        if transaction_id is not None:
            self.transaction_id = transaction_id
        return self

    def with_deposit_id(self, deposit_id: str) -> Self:
        self.search_builder.deposit_id = deposit_id
        return self

    def with_settlement_dispute_id(self, settlement_dispute_id: str) -> Self:
        self.search_builder.settlement_dispute_id = settlement_dispute_id
        return self

    def where(
        self, criteria_enum: Optional[SearchCriteria], value: Any
    ) -> SearchCriteriaBuilder:  # Returns SearchCriteriaBuilder
        if criteria_enum is not None and value is not None:
            criteria = criteria_enum.value
            if self.search_criteria is None:
                self.search_criteria = {}
            self.search_criteria[criteria] = value
            self.search_builder.and_with(criteria_enum, value)
        return self.search_builder

    def order_by(
        self, sort_property: Any, sort_direction: SortDirection = SortDirection.DESC
    ) -> Self:
        self.order = sort_direction

        if self.report_type == ReportType.FindStoredPaymentMethodsPaged:
            self.stored_payment_method_order_by = sort_property
        elif self.report_type in [
            ReportType.FindTransactions,
            ReportType.FindTransactionsPaged,
            ReportType.FindSettlementTransactionsPaged,
        ]:
            self.transaction_order_by = sort_property
        elif self.report_type in [
            ReportType.FindDeposits,
            ReportType.FindDepositsPaged,
        ]:
            self.deposit_order_by = sort_property
        elif self.report_type in [
            ReportType.FindDisputesPaged,
            ReportType.FindSettlementDisputesPaged,
        ]:
            self.dispute_order_by = sort_property
        else:
            raise NotImplementedError()

        return self

    def setup_validations(self):
        # TransactionDetail validation
        self.validations.of(ReportType.TransactionDetail).check(
            "transaction_id"
        ).is_not_none().check("transaction_id").is_not_none().check(
            "device_id"
        ).is_none().check(
            "start_date"
        ).is_none().check(
            "end_date"
        ).is_none()

        # Activity validation
        self.validations.of(ReportType.Activity).check("transaction_id").is_none()

        # DocumentDisputeDetail validation
        self.validations.of(ReportType.DocumentDisputeDetail).check(
            "search_builder.dispute_document_id"
        ).is_not_none().check("search_builder.dispute_id").is_not_none()
