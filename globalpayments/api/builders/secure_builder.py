from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Dict, Any, Optional, Self

from globalpayments.api.entities import (
    Address,
    TransactionType,
)
from globalpayments.api.entities.browser_data import BrowserData
from globalpayments.api.entities.enums import (
    AddressType,
    AgeIndicator,
    AuthenticationSource,
    CustomerAuthenticationMethod,
    DeliveryTimeFrame,
    OrderTransactionType,
    PhoneNumberType,
    PreOrderIndicator,
    PriorAuthenticationMethod,
    ReorderIndicator,
    ShippingMethod,
)
from . import BaseBuilder
from ..entities.phone_number import PhoneNumber


class SecureBuilder(BaseBuilder, ABC):
    def __init__(self):
        super().__init__()
        self.amount: Optional[float] = None
        self.currency: Optional[str] = None
        self.order_create_date: Optional[str] = None
        self.order_transaction_type: Optional[OrderTransactionType] = None
        self.order_id: Optional[str] = None
        self.reference_number: Optional[str] = None
        self.address_match_indicator: Optional[bool] = None
        self.shipping_address: Optional[Address] = None
        self.shipping_method: Optional[ShippingMethod] = None
        self.shipping_name_matches_card_holder_name: Optional[bool] = None
        self.shipping_address_create_date: Optional[date] = None
        self.shipping_address_usage_indicator: Optional[AgeIndicator] = None
        self.gift_card_amount: Optional[float] = None
        self.gift_card_count: Optional[int] = None
        self.gift_card_currency: Optional[str] = None
        self.delivery_email: Optional[str] = None
        self.delivery_timeframe: Optional[DeliveryTimeFrame] = None
        self.pre_order_availability_date: Optional[date] = None
        self.pre_order_indicator: Optional[PreOrderIndicator] = None
        self.reorder_indicator: Optional[ReorderIndicator] = None
        self.customer_account_id: Optional[str] = None
        self.account_age_indicator: Optional[AgeIndicator] = None
        self.account_change_date: Optional[date] = None
        self.account_create_date: Optional[date] = None
        self.account_change_indicator: Optional[AgeIndicator] = None
        self.password_change_date: Optional[date] = None
        self.password_change_indicator: Optional[AgeIndicator] = None
        self.phone_list: Dict[PhoneNumberType, Any] = {}
        self.home_country_code: Optional[str] = None
        self.home_number: Optional[str] = None
        self.work_country_code: Optional[str] = None
        self.work_number: Optional[str] = None
        self.mobile_country_code: Optional[str] = None
        self.mobile_number: Optional[str] = None
        self.payment_account_create_date: Optional[date] = None
        self.payment_age_indicator: Optional[AgeIndicator] = None
        self.previous_suspicious_activity: Optional[bool] = None
        self.number_of_purchases_in_last_six_months: Optional[int] = None
        self.number_of_transactions_in_last_24_hours: Optional[int] = None
        self.number_of_add_card_attempts_in_last_24_hours: Optional[int] = None
        self.number_of_transactions_in_last_year: Optional[int] = None
        self.browser_data: Optional[BrowserData] = None
        self.prior_authentication_data: Optional[str] = None
        self.prior_authentication_method: Optional[PriorAuthenticationMethod] = None
        self.prior_authentication_transaction_id: Optional[str] = None
        self.prior_authentication_timestamp: Optional[datetime] = None
        self.max_number_of_installments: Optional[int] = None
        self.recurring_authorization_expiry_date: Optional[date] = None
        self.recurring_authorization_frequency: Optional[int] = None
        self.customer_authentication_data: Optional[str] = None
        self.customer_authentication_method: Optional[CustomerAuthenticationMethod] = (
            None
        )
        self.customer_authentication_timestamp: Optional[datetime] = None
        self.idempotency_key: Optional[str] = None
        self.authentication_source: Optional[AuthenticationSource] = None
        self.payment_method: Optional[Any] = None
        self.billing_address: Optional[Address] = None

    @abstractmethod
    def with_payment_method(self, value: Any) -> Self:
        pass

    def with_transaction_type(self, transaction_type: TransactionType) -> Self:
        self.transaction_type = transaction_type
        return self

    def with_amount(self, value: float) -> Self:
        self.amount = value
        return self

    def with_currency(self, value: str) -> Self:
        self.currency = value
        return self

    def with_authentication_source(self, value: AuthenticationSource) -> Self:
        self.authentication_source = value
        return self

    def with_order_create_date(self, value: str) -> Self:
        self.order_create_date = value
        return self

    def with_reference_number(self, reference_number: str) -> Self:
        self.reference_number = reference_number
        return self

    def with_address_match_indicator(self, value: bool) -> Self:
        self.address_match_indicator = value
        return self

    def with_address(
        self, address: Address, type: AddressType = AddressType.Billing
    ) -> Self:
        if type == AddressType.Billing:
            self.billing_address = address
        else:
            self.shipping_address = address
        return self

    def with_gift_card_amount(self, gift_card_amount: float) -> Self:
        self.gift_card_amount = gift_card_amount
        return self

    def with_gift_card_count(self, gift_card_count: int) -> Self:
        self.gift_card_count = gift_card_count
        return self

    def with_gift_card_currency(self, gift_card_currency: str) -> Self:
        self.gift_card_currency = gift_card_currency
        return self

    def with_delivery_email(self, delivery_email: str) -> Self:
        self.delivery_email = delivery_email
        return self

    def with_delivery_time_frame(self, delivery_timeframe: DeliveryTimeFrame) -> Self:
        self.delivery_timeframe = delivery_timeframe
        return self

    def with_shipping_method(self, shipping_method: ShippingMethod) -> Self:
        self.shipping_method = shipping_method
        return self

    def with_shipping_name_matches_card_holder_name(
        self, shipping_name_matches_card_holder_name: bool
    ) -> Self:
        self.shipping_name_matches_card_holder_name = (
            shipping_name_matches_card_holder_name
        )
        return self

    def with_shipping_address_create_date(
        self, shipping_address_create_date: date
    ) -> Self:
        self.shipping_address_create_date = shipping_address_create_date
        return self

    def with_shipping_address_usage_indicator(
        self, shipping_address_usage_indicator: AgeIndicator
    ) -> Self:
        self.shipping_address_usage_indicator = shipping_address_usage_indicator
        return self

    def with_pre_order_availability_date(
        self, pre_order_availability_date: date
    ) -> Self:
        self.pre_order_availability_date = pre_order_availability_date
        return self

    def with_pre_order_indicator(self, pre_order_indicator: PreOrderIndicator) -> Self:
        self.pre_order_indicator = pre_order_indicator
        return self

    def with_reorder_indicator(self, reorder_indicator: ReorderIndicator) -> Self:
        self.reorder_indicator = reorder_indicator
        return self

    def with_order_transaction_type(
        self, order_transaction_type: OrderTransactionType
    ) -> Self:
        self.order_transaction_type = order_transaction_type
        return self

    def with_order_id(self, value: str) -> Self:
        self.order_id = value
        return self

    def with_customer_account_id(self, customer_account_id: str) -> Self:
        self.customer_account_id = customer_account_id
        return self

    def with_account_age_indicator(self, age_indicator: AgeIndicator) -> Self:
        self.account_age_indicator = age_indicator
        return self

    def with_account_change_date(self, account_change_date: date) -> Self:
        self.account_change_date = account_change_date
        return self

    def with_account_create_date(self, account_create_date: date) -> Self:
        self.account_create_date = account_create_date
        return self

    def with_account_change_indicator(
        self, account_change_indicator: AgeIndicator
    ) -> Self:
        self.account_change_indicator = account_change_indicator
        return self

    def with_password_change_date(self, password_change_date: date) -> Self:
        self.password_change_date = password_change_date
        return self

    def with_password_change_indicator(
        self, password_change_indicator: AgeIndicator
    ) -> Self:
        self.password_change_indicator = password_change_indicator
        return self

    def with_phone_number(
        self, phone_country_code: str, number: str, type: PhoneNumberType
    ) -> Self:
        phone_number = PhoneNumber(phone_country_code, number, type)
        self.phone_list[type] = phone_number

        if phone_number.type == PhoneNumberType.HOME:
            self.home_number = number
            self.home_country_code = phone_country_code
        elif phone_number.type == PhoneNumberType.WORK:
            self.work_number = number
            self.work_country_code = phone_country_code
        elif phone_number.type == PhoneNumberType.MOBILE:
            self.mobile_number = number
            self.mobile_country_code = phone_country_code

        return self

    # Deprecated methods - will keep for backward compatibility
    def with_home_number(self, country_code: str, number: str) -> Self:
        self.home_country_code = country_code
        self.home_number = number
        return self

    def with_work_number(self, country_code: str, number: str) -> Self:
        self.work_country_code = country_code
        self.work_number = number
        return self

    def with_mobile_number(self, country_code: str, number: str) -> Self:
        self.mobile_country_code = country_code
        self.mobile_number = number
        return self

    def with_payment_account_create_date(
        self, payment_account_create_date: date
    ) -> Self:
        self.payment_account_create_date = payment_account_create_date
        return self

    def with_payment_account_age_indicator(
        self, payment_age_indicator: AgeIndicator
    ) -> Self:
        self.payment_age_indicator = payment_age_indicator
        return self

    def with_previous_suspicious_activity(
        self, previous_suspicious_activity: bool
    ) -> Self:
        self.previous_suspicious_activity = previous_suspicious_activity
        return self

    def with_number_of_purchases_in_last_six_months(
        self, number_of_purchases_in_last_six_months: int
    ) -> Self:
        self.number_of_purchases_in_last_six_months = (
            number_of_purchases_in_last_six_months
        )
        return self

    def with_number_of_transactions_in_last_24_hours(
        self, number_of_transactions_in_last_24_hours: int
    ) -> Self:
        self.number_of_transactions_in_last_24_hours = (
            number_of_transactions_in_last_24_hours
        )
        return self

    def with_number_of_add_card_attempts_in_last_24_hours(
        self, number_of_add_card_attempts_in_last_24_hours: int
    ) -> Self:
        self.number_of_add_card_attempts_in_last_24_hours = (
            number_of_add_card_attempts_in_last_24_hours
        )
        return self

    def with_number_of_transactions_in_last_year(
        self, number_of_transactions_in_last_year: int
    ) -> Self:
        self.number_of_transactions_in_last_year = number_of_transactions_in_last_year
        return self

    def with_browser_data(self, value: BrowserData) -> Self:
        self.browser_data = value
        return self

    def with_prior_authentication_data(self, prior_authentication_data: str) -> Self:
        self.prior_authentication_data = prior_authentication_data
        return self

    def with_prior_authentication_method(
        self, prior_authentication_method: PriorAuthenticationMethod
    ) -> Self:
        self.prior_authentication_method = prior_authentication_method
        return self

    def with_prior_authentication_transaction_id(
        self, prior_authentication_transaction_id: str
    ) -> Self:
        self.prior_authentication_transaction_id = prior_authentication_transaction_id
        return self

    def with_prior_authentication_timestamp(
        self, prior_authentication_timestamp: datetime
    ) -> Self:
        self.prior_authentication_timestamp = prior_authentication_timestamp
        return self

    def with_max_number_of_installments(self, max_number_of_installments: int) -> Self:
        self.max_number_of_installments = max_number_of_installments
        return self

    def with_recurring_authorization_expiry_date(
        self, recurring_authorization_expiry_date: date
    ) -> Self:
        self.recurring_authorization_expiry_date = recurring_authorization_expiry_date
        return self

    def with_recurring_authorization_frequency(
        self, recurring_authorization_frequency: int
    ) -> Self:
        self.recurring_authorization_frequency = recurring_authorization_frequency
        return self

    def with_customer_authentication_data(
        self, customer_authentication_data: str
    ) -> Self:
        self.customer_authentication_data = customer_authentication_data
        return self

    def with_customer_authentication_method(
        self, customer_authentication_method: CustomerAuthenticationMethod
    ) -> Self:
        self.customer_authentication_method = customer_authentication_method
        return self

    def with_customer_authentication_timestamp(
        self, customer_authentication_timestamp: datetime
    ) -> Self:
        self.customer_authentication_timestamp = customer_authentication_timestamp
        return self

    def with_idempotency_key(self, value: str) -> Self:
        self.idempotency_key = value
        return self

    def get_amount(self):
        if self.amount is not None:
            return self.amount
        return None

    def get_currency(self):
        return self.currency

    def get_prior_authentication_method(self):
        return self.prior_authentication_method

    def get_prior_authentication_transaction_id(self):
        return self.prior_authentication_transaction_id

    def get_prior_authentication_timestamp(self):
        return self.prior_authentication_timestamp

    def get_prior_authentication_data(self):
        return self.prior_authentication_data

    def get_max_number_of_installments(self):
        return self.max_number_of_installments

    def get_recurring_authorization_frequency(self):
        return self.recurring_authorization_frequency

    def get_recurring_authorization_expiry_date(self):
        return self.recurring_authorization_expiry_date

    def get_customer_authentication_data(self):
        return self.customer_authentication_data

    def get_customer_authentication_timestamp(self):
        return self.customer_authentication_timestamp

    def get_customer_authentication_method(self):
        return self.customer_authentication_method
