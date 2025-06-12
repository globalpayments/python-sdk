from typing import Optional, List, Self

from globalpayments.api.entities import (
    ThreeDSecure,
    TransactionType,
)
from .secure_builder import SecureBuilder

# Delay import of ServicesContainer
from ..entities.enums import (
    TransactionModifier,
    AuthenticationSource,
    ThreeDSecureVersion,
    AuthenticationRequestType,
    ChallengeRequestIndicator,
    MessageCategory,
    MessageVersion,
    MethodUrlCompletion,
    SdkInterface,
    SdkUiType,
    AgeIndicator,
)
from ..entities.exceptions import BuilderException
from ..entities.merchant_data_collection import MerchantDataCollection
from ..entities.mobile_data import MobileData
from ..entities.stored_credentials import StoredCredential

# Delay import of GpApiConnector
from ..payment_methods import PaymentMethod
from ..utils import StringUtils


class Secure3dBuilder(SecureBuilder):
    def __init__(self, transaction_type: TransactionType):
        super().__init__()
        self._transaction_type: TransactionType = transaction_type
        self.application_id: Optional[str] = None
        self.authentication_request_type: Optional[AuthenticationRequestType] = (
            AuthenticationRequestType.PaymentTransaction
        )
        self.challenge_request_indicator: Optional[ChallengeRequestIndicator] = None
        self.customer_email: Optional[str] = None
        self.decoupled_flow_request: Optional[bool] = None
        self.decoupled_flow_timeout: Optional[int] = None
        self.decoupled_notification_url: Optional[str] = None
        self.encoded_data: Optional[str] = None
        self.ephemeral_public_key: Optional[str] = None
        self.maximum_timeout: Optional[int] = None
        self.merchant_data: Optional[MerchantDataCollection] = None
        self.message_category: Optional[MessageCategory] = (
            MessageCategory.PaymentAuthentication
        )
        self.merchant_initiated_request_type: Optional[AuthenticationRequestType] = None
        self.message_version: Optional[MessageVersion] = None
        self.method_url_completion: Optional[MethodUrlCompletion] = None
        self.payer_authentication_response: Optional[str] = None
        self.sdk_interface: Optional[SdkInterface] = None
        self.sdk_transaction_id: Optional[str] = None
        self.sdk_ui_types: Optional[List[SdkUiType]] = None
        self.three_d_secure: Optional[ThreeDSecure] = None
        self.transaction_modifier: TransactionModifier = TransactionModifier.NoModifier
        self.whitelist_status: Optional[str] = None
        self.enable_exemption_optimization: Optional[bool] = None
        self.mobile_data: Optional[MobileData] = None
        self.stored_credential: Optional[StoredCredential] = None
        self.authentication_source = AuthenticationSource.Browser

    @property
    def transaction_type(self) -> TransactionType:
        return self._transaction_type

    def has_mobile_fields(self) -> bool:
        return (
            self.application_id is not None
            and self.application_id != ""
            or self.ephemeral_public_key is not None
            and self.ephemeral_public_key != ""
            or self.maximum_timeout is not None
            and self.maximum_timeout != 0
            or self.sdk_transaction_id is not None
            and self.sdk_transaction_id != ""
            or self.encoded_data is not None
            and self.encoded_data != ""
            or self.sdk_interface is not None
            or self.sdk_ui_types is not None
        )

    def has_prior_authentication_data(self) -> bool:
        prior_auth_method = self.get_prior_authentication_method()
        prior_auth_transaction_id = self.get_prior_authentication_transaction_id()
        prior_auth_timestamp = self.get_prior_authentication_timestamp()
        prior_auth_data = self.get_prior_authentication_data()

        return (
            prior_auth_method is not None
            or (
                prior_auth_transaction_id is not None
                and prior_auth_transaction_id != ""
            )
            or prior_auth_timestamp is not None
            or (prior_auth_data is not None and prior_auth_data != "")
        )

    def has_recurring_auth_data(self) -> bool:
        return (
            self.get_max_number_of_installments() is not None
            or self.get_recurring_authorization_frequency() is not None
            or self.get_recurring_authorization_expiry_date() is not None
        )

    def has_payer_login_data(self) -> bool:
        customer_auth_data = self.get_customer_authentication_data()
        customer_auth_timestamp = self.get_customer_authentication_timestamp()
        customer_auth_method = self.get_customer_authentication_method()

        return (
            (customer_auth_data is not None and customer_auth_data != "")
            or customer_auth_timestamp is not None
            or customer_auth_method is not None
        )

    def with_payment_method(self, value: Optional[PaymentMethod]) -> Self:
        self.payment_method = value
        if self.payment_method is not None and getattr(
            self.payment_method, "is_secure_3d"
        ):
            secure_ecom = getattr(self.payment_method, "three_d_secure")
            if secure_ecom is not None:
                self.three_d_secure = secure_ecom
        return self

    def with_application_id(self, application_id: str) -> Self:
        self.application_id = application_id
        return self

    def with_authentication_request_type(
        self, value: AuthenticationRequestType
    ) -> Self:
        self.authentication_request_type = value
        return self

    def with_challenge_request_indicator(
        self, challenge_request_indicator: ChallengeRequestIndicator
    ) -> Self:
        self.challenge_request_indicator = challenge_request_indicator
        return self

    def with_customer_email(self, value: str) -> Self:
        self.customer_email = value
        return self

    def with_decoupled_flow_request(self, decoupled_flow_request: bool) -> Self:
        self.decoupled_flow_request = decoupled_flow_request
        return self

    def with_decoupled_flow_timeout(self, decoupled_flow_timeout: int) -> Self:
        self.decoupled_flow_timeout = decoupled_flow_timeout
        return self

    def with_decoupled_notification_url(self, decoupled_notification_url: str) -> Self:
        self.decoupled_notification_url = decoupled_notification_url
        return self

    def with_encoded_data(self, encoded_data: str) -> Self:
        self.encoded_data = encoded_data
        return self

    def with_ephemeral_public_key(self, ephemeral_public_key: str) -> Self:
        self.ephemeral_public_key = ephemeral_public_key
        return self

    def with_maximum_timeout(self, maximum_timeout: int) -> Self:
        self.maximum_timeout = maximum_timeout
        return self

    def with_merchant_data(self, value: MerchantDataCollection) -> Self:
        self.merchant_data = value
        if self.merchant_data is not None:
            if self.three_d_secure is None:
                self.three_d_secure = ThreeDSecure()
            self.three_d_secure.set_merchant_data(value)
        return self

    def with_message_category(self, value: MessageCategory) -> Self:
        self.message_category = value
        return self

    def with_merchant_initiated_request_type(
        self, merchant_initiated_request_type: AuthenticationRequestType
    ) -> Self:
        self.merchant_initiated_request_type = merchant_initiated_request_type
        return self

    def with_message_version(self, value: MessageVersion) -> Self:
        self.message_version = value
        return self

    def with_method_url_completion(self, value: MethodUrlCompletion) -> Self:
        self.method_url_completion = value
        return self

    def with_payer_authentication_response(self, value: str) -> Self:
        self.payer_authentication_response = value
        return self

    def with_sdk_interface(self, sdk_interface: SdkInterface) -> Self:
        self.sdk_interface = sdk_interface
        return self

    def with_sdk_transaction_id(self, sdk_transaction_id: str) -> Self:
        self.sdk_transaction_id = sdk_transaction_id
        return self

    def with_sdk_ui_types(self, sdk_ui_types: List[SdkUiType]) -> Self:
        self.sdk_ui_types = sdk_ui_types
        return self

    def with_server_transaction_id(self, value: str) -> Self:
        if not self.three_d_secure:
            self.three_d_secure = ThreeDSecure()
        self.three_d_secure.server_transaction_id = value
        return self

    def with_three_d_secure(self, three_d_secure: ThreeDSecure) -> Self:
        self.three_d_secure = three_d_secure
        return self

    def with_whitelist_status(self, whitelist_status: bool) -> Self:
        self.whitelist_status = "TRUE" if whitelist_status else "FALSE"
        return self

    def with_stored_credential(self, stored_credential: StoredCredential) -> Self:
        self.stored_credential = stored_credential
        return self

    def with_enable_exemption_optimization(self, value: bool) -> Self:
        self.enable_exemption_optimization = value
        return self

    def with_mobile_data(self, value: MobileData) -> Self:
        self.mobile_data = value
        return self

    def execute(
        self,
        config_name: Optional[str] = "default",
        version: ThreeDSecureVersion = ThreeDSecureVersion.Two,
    ) -> ThreeDSecure:
        # Import here to avoid circular imports
        from .. import ServicesContainer
        from ..gateways import GpApiConnector

        # Call parent execute method
        super().execute()

        # Setup return object
        rvalue = self.three_d_secure
        if not rvalue:
            rvalue = ThreeDSecure()
            rvalue.version = version

        # Working version
        if rvalue.version:
            version = rvalue.version
        # Get the provider
        provider = ServicesContainer.instance().get_secure_3d(config_name, version)
        if version == ThreeDSecureVersion.One and (
            isinstance(provider, GpApiConnector)
        ):
            raise BuilderException(f"3D Secure {version} is no longer supported!")

        if provider:
            can_downgrade = False
            if (
                provider.get_version() == ThreeDSecureVersion.Two
                and version == ThreeDSecureVersion.Any
                and not (isinstance(provider, GpApiConnector))
            ):
                try:
                    one_provider = ServicesContainer.instance().get_secure_3d(
                        config_name, ThreeDSecureVersion.One
                    )
                    can_downgrade = one_provider is not None
                except Exception:
                    # NOT CONFIGURED
                    pass

            # Process the request, capture any exceptions which might have been thrown
            response = None
            try:
                response = provider.process_secure_3d(self)

                if not response and can_downgrade:
                    return self.execute(config_name, ThreeDSecureVersion.One)
            except Exception as exc:
                # Check for not enrolled
                if getattr(exc, "response_code", None) is not None:
                    if (
                        getattr(exc, "response_code", "") == "110"
                        and provider.get_version() == ThreeDSecureVersion.One
                    ):
                        return rvalue
                    # Import GpApiConnector here to avoid circular import
                    from ..gateways import GpApiConnector

                    if isinstance(provider, GpApiConnector):
                        raise exc
                elif (
                    can_downgrade
                    and self._transaction_type == TransactionType.VerifyEnrolled
                ):
                    return self.execute(config_name, ThreeDSecureVersion.One)
                else:
                    # Throw exception
                    raise exc

            # Check the response
            if response:
                if self._transaction_type == TransactionType.VerifyEnrolled:
                    if hasattr(response, "three_d_secure") and response.three_d_secure:
                        rvalue = response.three_d_secure
                        if rvalue.enrolled in ["True", "Y", True]:
                            rvalue.amount = StringUtils.to_dollar_string(
                                self.get_amount()
                            )
                            rvalue.currency = self.get_currency()
                            rvalue.order_id = response.order_id
                            rvalue.version = ThreeDSecureVersion.Two
                        elif can_downgrade:
                            return self.execute(config_name, ThreeDSecureVersion.One)
                    elif can_downgrade:
                        return self.execute(config_name, ThreeDSecureVersion.One)
                elif self._transaction_type in [
                    TransactionType.InitiateAuthentication,
                    TransactionType.VerifySignature,
                ]:
                    rvalue.merge(response.three_d_secure)

        return rvalue

    def setup_validations(self):
        # VerifyEnrolled validations
        self.validations.of(TransactionType.VerifyEnrolled).check(
            "payment_method"
        ).is_not_none()

        # VerifySignature validations
        self.validations.of(TransactionType.VerifySignature).with_constraint(
            "version", ThreeDSecureVersion.One
        ).check("three_d_secure").is_not_none().with_constraint(
            "version", ThreeDSecureVersion.One
        ).check(
            "payer_authentication_response"
        ).is_not_none()

        self.validations.of(TransactionType.VerifySignature).when(
            "version"
        ).is_equal_to(ThreeDSecureVersion.Two).check(
            "three_d_secure.server_transaction_id"
        ).is_not_none()

        # InitiateAuthentication validations
        self.validations.of(TransactionType.InitiateAuthentication).check(
            "three_d_secure"
        ).is_not_none()

        self.validations.of(TransactionType.InitiateAuthentication).when(
            "merchant_initiated_request_type"
        ).is_not_none().check("merchant_initiated_request_type").is_not_equal_to(
            AuthenticationRequestType.PaymentTransaction
        )

        self.validations.of(TransactionType.InitiateAuthentication).when(
            "account_age_indicator"
        ).is_not_none().check("account_age_indicator").is_not_equal_to(
            AgeIndicator.NoAccount
        )

        self.validations.of(TransactionType.InitiateAuthentication).when(
            "password_change_indicator"
        ).is_not_none().check("password_change_indicator").is_not_equal_to(
            AgeIndicator.NoAccount
        )

        self.validations.of(TransactionType.InitiateAuthentication).when(
            "shipping_address_usage_indicator"
        ).is_not_none().check("shipping_address_usage_indicator").is_not_equal_to(
            AgeIndicator.NoAccount
        ).when(
            "shipping_address_usage_indicator"
        ).is_not_none().check(
            "shipping_address_usage_indicator"
        ).is_not_equal_to(
            AgeIndicator.NoAccount
        )
