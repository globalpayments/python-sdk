"""
Secure request builder for Global Payments API
"""

import json
from typing import Any, Dict, Optional

from globalpayments.api.builders.request_builder.IRequestBuilder import IRequestBuilder
from globalpayments.api.entities.enums import (
    TransactionType,
    HttpVerb,
    DecoupledFlowRequest,
    DateFormat,
)
from globalpayments.api.entities.gp_api.gp_api_request import GpApiRequest
from globalpayments.api.utils import StringUtils, GenerationUtils
from globalpayments.api.utils.serializer import object_serialize
from globalpayments.api.utils.time import format_time


class GpApiSecureRequestBuilder(IRequestBuilder):
    """
    Builds secure requests for the Global Payments API
    """

    def __init__(self):
        """
        Initialize the secure request builder
        """
        self.masked_values: Dict[str, str] = {}

    def _set_order_param(self, builder: Any) -> Optional[Dict[str, Any]]:
        """
        Sets order parameters
        """
        preorder_availability_date = None
        pre_order_date = getattr(builder, "pre_order_availability_date", None)
        if pre_order_date:
            preorder_availability_date = pre_order_date.strftime("%Y-%m-%d")

        order_create_date = getattr(builder, "order_create_date", None)
        time_created_reference = None
        if order_create_date:
            time_created_reference = format_time(
                order_create_date, DateFormat.ISO_8601_UTC
            )

        order = {
            "time_created_reference": StringUtils.convert_enum_value(
                time_created_reference
            ),
            "amount": StringUtils.convert_enum_value(
                StringUtils.to_numeric(str(getattr(builder, "amount", 0)))
            ),
            "currency": StringUtils.convert_enum_value(
                getattr(builder, "currency", None)
            ),
            "reference": StringUtils.convert_enum_value(
                getattr(builder, "order_id", None) or GenerationUtils.get_uuid()
            ),
            "address_match_indicator": StringUtils.convert_enum_value(
                StringUtils.bool_to_string(
                    getattr(builder, "address_match_indicator", None)
                )
                if getattr(builder, "address_match_indicator", None) is not None
                else None
            ),
            "gift_card_count": StringUtils.convert_enum_value(
                getattr(builder, "gift_card_count", None)
            ),
            "gift_card_currency": StringUtils.convert_enum_value(
                getattr(builder, "gift_card_currency", None)
            ),
            "gift_card_amount": StringUtils.convert_enum_value(
                getattr(builder, "gift_card_amount", None)
            ),
            "delivery_email": StringUtils.convert_enum_value(
                getattr(builder, "delivery_email", None)
            ),
            "delivery_timeframe": StringUtils.convert_enum_value(
                getattr(builder, "delivery_timeframe", None)
            ),
            "shipping_method": StringUtils.convert_enum_value(
                getattr(builder, "shipping_method", None)
            ),
            "shipping_name_matches_cardholder_name": StringUtils.convert_enum_value(
                StringUtils.bool_to_string(
                    getattr(builder, "shipping_name_matches_cardholder_name", None)
                )
                if getattr(builder, "shipping_name_matches_cardholder_name", None)
                is not None
                else None
            ),
            "preorder_indicator": StringUtils.convert_enum_value(
                getattr(builder, "preorder_indicator", None)
            ),
            "preorder_availability_date": StringUtils.convert_enum_value(
                preorder_availability_date
            ),
            "category": StringUtils.convert_enum_value(
                getattr(builder, "order_transaction_type", None)
            ),
        }

        # Add shipping address if present
        shipping_address = getattr(builder, "shipping_address", None)
        if shipping_address:
            order["shipping_address"] = {
                "line1": StringUtils.convert_enum_value(
                    getattr(shipping_address, "street_address_1", None)
                ),
                "line2": StringUtils.convert_enum_value(
                    getattr(shipping_address, "street_address_2", None)
                ),
                "line3": StringUtils.convert_enum_value(
                    getattr(shipping_address, "street_address_3", None)
                ),
                "city": StringUtils.convert_enum_value(
                    getattr(shipping_address, "city", None)
                ),
                "postal_code": StringUtils.convert_enum_value(
                    getattr(shipping_address, "postal_code", None)
                ),
                "state": StringUtils.convert_enum_value(
                    getattr(shipping_address, "state", None)
                ),
                "country": StringUtils.convert_enum_value(
                    getattr(shipping_address, "country_code", None)
                ),
            }

        return order if not self._are_all_keys_undefined(order) else None

    def _set_payer_param(self, builder: Any) -> Optional[Dict[str, Any]]:
        """
        Sets payer parameters
        """
        account_creation_date = None
        account_create_date = getattr(builder, "account_create_date", None)
        if account_create_date:
            account_creation_date = account_create_date.strftime("%Y-%m-%d")

        account_change_date = None
        account_change_date_val = getattr(builder, "account_change_date", None)
        if account_change_date_val:
            account_change_date = account_change_date_val.strftime("%Y-%m-%d")

        account_password_change_date = None
        password_change_date = getattr(builder, "password_change_date", None)
        if password_change_date:
            account_password_change_date = password_change_date.strftime("%Y-%m-%d")

        payment_account_creation_date = None
        payment_account_create_date = getattr(
            builder, "payment_account_create_date", None
        )
        if payment_account_create_date:
            payment_account_creation_date = payment_account_create_date.strftime(
                "%Y-%m-%d"
            )

        provision_attempt_last_24hours_count = None
        add_card_attempts = getattr(
            builder, "number_of_add_card_attempts_in_last_24_hours", None
        )
        if add_card_attempts:
            provision_attempt_last_24hours_count = add_card_attempts.strftime(
                "%Y-%m-%d"
            )

        # Phone numbers
        home_phone = None
        home_country_code = getattr(builder, "home_country_code", None)
        home_number = getattr(builder, "home_number", None)
        if home_country_code or home_number:
            home_phone = {
                "country_code": StringUtils.convert_enum_value(home_country_code),
                "subscriber_number": StringUtils.convert_enum_value(home_number),
            }

        work_phone = None
        work_country_code = getattr(builder, "work_country_code", None)
        work_number = getattr(builder, "work_number", None)
        if work_country_code or work_number:
            work_phone = {
                "country_code": StringUtils.convert_enum_value(work_country_code),
                "subscriber_number": StringUtils.convert_enum_value(work_number),
            }

        mobile_phone = None
        mobile_country_code = getattr(builder, "mobile_country_code", None)
        mobile_number = getattr(builder, "mobile_number", None)
        if mobile_country_code or mobile_number:
            mobile_phone = {
                "country_code": StringUtils.convert_enum_value(mobile_country_code),
                "subscriber_number": StringUtils.convert_enum_value(mobile_number),
            }

        account_age_indicator = getattr(builder, "account_age_indicator", None)
        account_change_indicator = getattr(builder, "account_change_indicator", None)
        password_change_indicator = getattr(builder, "password_change_indicator", None)
        payment_age_indicator = getattr(builder, "payment_age_indicator", None)
        shipping_address_usage_indicator = getattr(
            builder, "shipping_address_usage_indicator", None
        )

        shipping_address_time_created_reference = None
        shipping_address_create_date = getattr(
            builder, "shipping_address_create_date", None
        )
        if shipping_address_create_date:
            shipping_address_time_created_reference = format_time(
                shipping_address_create_date, DateFormat.ISO_8601_UTC
            )

        purchases_count = getattr(
            builder, "number_of_purchases_in_last_six_months", None
        )
        transactions_24h_count = getattr(
            builder, "number_of_transactions_in_last_24_hours", None
        )
        transactions_year_count = getattr(
            builder, "number_of_transactions_in_last_year", None
        )

        payer = {
            "reference": StringUtils.convert_enum_value(
                getattr(builder, "customer_account_id", None)
            ),
            "account_age": StringUtils.convert_enum_value(
                str(account_age_indicator) if account_age_indicator else None
            ),
            "account_creation_date": StringUtils.convert_enum_value(
                account_creation_date
            ),
            "account_change_date": StringUtils.convert_enum_value(account_change_date),
            "account_change_indicator": StringUtils.convert_enum_value(
                account_change_indicator if account_change_indicator else None
            ),
            "account_password_change_date": StringUtils.convert_enum_value(
                account_password_change_date
            ),
            "account_password_change_indicator": StringUtils.convert_enum_value(
                password_change_indicator if password_change_indicator else None
            ),
            "home_phone": home_phone,
            "work_phone": work_phone,
            "mobile_phone": mobile_phone,
            "payment_account_creation_date": StringUtils.convert_enum_value(
                payment_account_creation_date
            ),
            "payment_account_age_indicator": StringUtils.convert_enum_value(
                payment_age_indicator if payment_age_indicator else None
            ),
            "suspicious_account_activity": StringUtils.convert_enum_value(
                StringUtils.bool_to_string(
                    getattr(builder, "previous_suspicious_activity", None)
                )
                if getattr(builder, "previous_suspicious_activity", None) is not None
                else None
            ),
            "purchases_last_6months_count": StringUtils.convert_enum_value(
                self._pad_number(purchases_count) if purchases_count else None
            ),
            "transactions_last_24hours_count": StringUtils.convert_enum_value(
                self._pad_number(transactions_24h_count)
                if transactions_24h_count
                else None
            ),
            "transaction_last_year_count": StringUtils.convert_enum_value(
                self._pad_number(transactions_year_count)
                if transactions_year_count
                else None
            ),
            "provision_attempt_last_24hours_count": StringUtils.convert_enum_value(
                provision_attempt_last_24hours_count
            ),
            "shipping_address_time_created_reference": StringUtils.convert_enum_value(
                shipping_address_time_created_reference
            ),
            "shipping_address_creation_indicator": StringUtils.convert_enum_value(
                shipping_address_usage_indicator
                if shipping_address_usage_indicator
                else None
            ),
            "email": StringUtils.convert_enum_value(
                getattr(builder, "customer_email", None)
            ),
        }

        return payer if not self._are_all_keys_undefined(payer) else None

    def _set_browser_data_param(self, browser_data: Any) -> Optional[Dict[str, Any]]:
        """
        Sets browser data parameters
        """
        if not browser_data:
            return None

        java_enabled = getattr(browser_data, "java_enabled", None)
        javascript_enabled = getattr(browser_data, "javascript_enabled", None)

        return {
            "accept_header": StringUtils.convert_enum_value(
                getattr(browser_data, "accept_header", None)
            ),
            "color_depth": StringUtils.convert_enum_value(
                getattr(browser_data, "color_depth", "")
            ),
            "ip": StringUtils.convert_enum_value(
                getattr(browser_data, "ip_address", None)
            ),  # Note: "ip" not "ip_address"
            "java_enabled": StringUtils.convert_enum_value(
                StringUtils.bool_to_string(java_enabled)
                if java_enabled is not None
                else None
            ),
            "javascript_enabled": StringUtils.convert_enum_value(
                StringUtils.bool_to_string(javascript_enabled)
                if javascript_enabled is not None
                else None
            ),
            "language": StringUtils.convert_enum_value(
                getattr(browser_data, "language", None)
            ),
            "screen_height": StringUtils.convert_enum_value(
                getattr(browser_data, "screen_height", None)
            ),
            "screen_width": StringUtils.convert_enum_value(
                getattr(browser_data, "screen_width", None)
            ),
            "challenge_window_size": StringUtils.convert_enum_value(
                getattr(browser_data, "challenge_window_size", "")
            ),
            "timezone": StringUtils.convert_enum_value(
                getattr(browser_data, "time_zone", "")
            ),
            "user_agent": StringUtils.convert_enum_value(
                getattr(browser_data, "user_agent", None)
            ),
        }

    def _set_payer_prior_3ds_authentication_data_param(
        self, builder: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Sets payer prior 3DS authentication data parameters
        """
        prior_auth_method = getattr(builder, "prior_authentication_method", None)
        prior_auth_timestamp = getattr(builder, "prior_authentication_timestamp", None)

        timestamp_iso = None
        if prior_auth_timestamp:
            timestamp_iso = format_time(prior_auth_timestamp, DateFormat.ISO_8601_UTC)

        payer_prior_3ds_auth_data = {
            "authentication_method": StringUtils.convert_enum_value(
                prior_auth_method if prior_auth_method else None
            ),
            "acs_transaction_reference": StringUtils.convert_enum_value(
                getattr(builder, "prior_authentication_transaction_id", None)
            ),
            "authentication_timestamp": StringUtils.convert_enum_value(timestamp_iso),
            "authentication_data": StringUtils.convert_enum_value(
                getattr(builder, "prior_authentication_data", None)
            ),
        }

        return (
            payer_prior_3ds_auth_data
            if not self._are_all_keys_undefined(payer_prior_3ds_auth_data)
            else None
        )

    def _set_recurring_authorization_data_param(
        self, builder: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Sets recurring authorization data parameters
        """
        max_installments = getattr(builder, "max_number_of_installments", None)

        recurring_auth_data = {
            "max_number_of_instalments": StringUtils.convert_enum_value(
                self._pad_number(max_installments) if max_installments else None
            ),
            "frequency": StringUtils.convert_enum_value(
                getattr(builder, "recurring_authorization_frequency", None)
            ),
            "expiry_date": StringUtils.convert_enum_value(
                getattr(builder, "recurring_authorization_expiry_date", None)
            ),
        }

        return (
            recurring_auth_data
            if not self._are_all_keys_undefined(recurring_auth_data)
            else None
        )

    def _set_payer_login_data_param(self, builder: Any) -> Optional[Dict[str, Any]]:
        """
        Sets payer login data parameters
        """
        authentication_timestamp = None
        customer_auth_timestamp = getattr(
            builder, "customer_authentication_timestamp", None
        )
        if customer_auth_timestamp:
            authentication_timestamp = customer_auth_timestamp.strftime("%Y-%m-%d")

        customer_auth_method = getattr(builder, "customer_authentication_method", None)

        payer_login_data = {
            "authentication_data": StringUtils.convert_enum_value(
                getattr(builder, "customer_authentication_data", None)
            ),
            "authentication_timestamp": StringUtils.convert_enum_value(
                authentication_timestamp
            ),
            "authentication_type": StringUtils.convert_enum_value(
                customer_auth_method if customer_auth_method else None
            ),
        }

        return (
            payer_login_data
            if not self._are_all_keys_undefined(payer_login_data)
            else None
        )

    def _are_all_keys_undefined(self, obj: Dict[str, Any]) -> bool:
        """
        Checks if all values in a dictionary are None or undefined
        """
        for value in obj.values():
            if value is not None:
                return False
        return True

    def _pad_number(self, num: int) -> str:
        """
        Pads a number to 2 digits with leading zeros
        """
        return str(num).zfill(2)

    def can_process(self, builder: Any) -> bool:
        """
        Determines if this builder can process the provided builder

        Args:
            builder: The builder to check

        Returns:
            True if this builder can process the provided builder, otherwise False
        """
        from globalpayments.api.builders.threeD_secure_builder import Secure3dBuilder

        return isinstance(builder, Secure3dBuilder)

    def build_request(self, builder: Any, config: Any = None) -> GpApiRequest:
        """
        Builds a request from the provided builder

        Args:
            builder: The secure 3D builder
            config: The GP API configuration

        Returns:
            A GpApiRequest object
        """
        if builder.transaction_type == TransactionType.VerifyEnrolled:
            return self.build_enrollment_request(builder, config)
        elif builder.transaction_type == TransactionType.InitiateAuthentication:
            return self.build_authentication_request(builder, config)
        elif builder.transaction_type == TransactionType.VerifySignature:
            return self.build_verification_request(builder, config)
        else:
            raise ValueError("Unsupported transaction type!")

    def build_enrollment_request(self, builder: Any, config: Any) -> GpApiRequest:
        """
        Builds an enrollment request

        Args:
            builder: The secure 3D builder
            config: The GP API configuration

        Returns:
            A GpApiRequest object
        """
        from globalpayments.api.utils import GenerationUtils

        request_data = {
            "account_name": StringUtils.convert_enum_value(
                config.access_token_info.transaction_processing_account_name
            ),
            "account_id": StringUtils.convert_enum_value(
                config.access_token_info.transaction_processing_account_id
            ),
            "channel": StringUtils.convert_enum_value(config.channel),
            "country": StringUtils.convert_enum_value(config.country),
            "reference": StringUtils.convert_enum_value(
                builder.reference_number
                if builder.reference_number
                else GenerationUtils.get_uuid()
            ),
            "amount": StringUtils.convert_enum_value(
                StringUtils.to_numeric(str(builder.amount))
            ),
            "currency": StringUtils.convert_enum_value(builder.currency),
            "preference": StringUtils.convert_enum_value(
                builder.challenge_request_indicator
            ),
            "source": StringUtils.convert_enum_value(
                builder.authentication_source if builder.authentication_source else None
            ),
            "payment_method": self._set_payment_method_param(builder.payment_method),
            "notifications": {
                "challenge_return_url": StringUtils.convert_enum_value(
                    config.challenge_notification_url
                ),
                "three_ds_method_return_url": StringUtils.convert_enum_value(
                    config.method_notification_url
                ),
                "decoupled_notification_url": StringUtils.convert_enum_value(
                    builder.decoupled_notification_url
                    if hasattr(builder, "decoupled_notification_url")
                    else None
                ),
            },
        }

        # Handle stored credential if present
        if hasattr(builder, "stored_credential") and builder.stored_credential:
            self._set_stored_credential_param(builder.stored_credential, request_data)

        # Filter out None values
        request_data = self.filter_none_values(request_data)

        GpApiRequest.masked_values = self.masked_values

        return GpApiRequest(
            GpApiRequest.AUTHENTICATIONS_ENDPOINT,
            HttpVerb.POST,
            object_serialize(request_data),
        )

    def build_authentication_request(self, builder: Any, config: Any) -> GpApiRequest:
        """
        Builds an authentication request

        Args:
            builder: The secure 3D builder
            config: The GP API configuration

        Returns:
            A GpApiRequest object
        """
        from globalpayments.api.utils.enum_mapping import EnumMapping
        from globalpayments.api.entities.enums import (
            GatewayProvider,
            AuthenticationSource,
        )

        request_data = {
            "three_ds": {
                "source": StringUtils.convert_enum_value(builder.authentication_source),
                "preference": StringUtils.convert_enum_value(
                    builder.challenge_request_indicator
                ),
                "message_version": StringUtils.convert_enum_value(
                    builder.three_d_secure.message_version
                ),
                "message_category": StringUtils.convert_enum_value(
                    EnumMapping.map_message_category(
                        GatewayProvider.GpApi,
                        builder.message_category,
                    )
                ),
            }
        }

        # Handle stored credential if present
        if hasattr(builder, "stored_credential") and builder.stored_credential:
            self._set_stored_credential_param(builder.stored_credential, request_data)

        request_data["method_url_completion_status"] = StringUtils.convert_enum_value(
            builder.method_url_completion
        )
        request_data["merchant_contact_url"] = StringUtils.convert_enum_value(
            config.merchant_contact_url
        )
        request_data["order"] = self._set_order_param(builder)
        request_data["payment_method"] = self._set_payment_method_param(
            builder.payment_method
        )
        request_data["payer"] = self._set_payer_param(builder)

        # Add billing address if present
        if hasattr(builder, "billing_address") and builder.billing_address:
            if "payer" not in request_data or request_data["payer"] is None:
                request_data["payer"] = {}
            request_data["payer"]["billing_address"] = {
                "line1": StringUtils.convert_enum_value(
                    builder.billing_address.street_address_1
                ),
                "line2": StringUtils.convert_enum_value(
                    builder.billing_address.street_address_2
                ),
                "line3": StringUtils.convert_enum_value(
                    builder.billing_address.street_address_3
                ),
                "city": StringUtils.convert_enum_value(builder.billing_address.city),
                "postal_code": StringUtils.convert_enum_value(
                    builder.billing_address.postal_code
                ),
                "state": StringUtils.convert_enum_value(builder.billing_address.state),
                "country": StringUtils.convert_enum_value(
                    getattr(builder.billing_address, "country_code", None)
                ),
            }

        request_data["payer_prior_three_ds_authentication_data"] = (
            self._set_payer_prior_3ds_authentication_data_param(builder)
        )
        request_data["recurring_authorization_data"] = (
            self._set_recurring_authorization_data_param(builder)
        )
        request_data["payer_login_data"] = self._set_payer_login_data_param(builder)

        # Add browser data if present and not mobile SDK
        if (
            hasattr(builder, "browser_data")
            and builder.browser_data
            and builder.authentication_source != AuthenticationSource.MobileSdk
        ):
            request_data["browser_data"] = self._set_browser_data_param(
                builder.browser_data
            )

        # Add mobile data if present and is mobile SDK
        if (
            hasattr(builder, "mobile_data")
            and builder.mobile_data
            and builder.authentication_source == AuthenticationSource.MobileSdk
        ):
            request_data["mobile_data"] = {
                "encoded_data": StringUtils.convert_enum_value(
                    builder.mobile_data.encoded_data
                ),
                "application_reference": StringUtils.convert_enum_value(
                    builder.mobile_data.application_reference
                ),
                "sdk_interface": StringUtils.convert_enum_value(
                    builder.mobile_data.sdk_interface
                ),
                "sdk_ui_type": StringUtils.convert_enum_value(
                    EnumMapping.map_sdk_ui_type(
                        GatewayProvider.GpApi,
                        builder.mobile_data.sdk_ui_types,
                    )
                ),
                "ephemeral_public_key": json.loads(
                    builder.mobile_data.ephemeral_public_key
                ),
                "maximum_timeout": StringUtils.convert_enum_value(
                    builder.mobile_data.maximum_timeout
                ),
                "reference_number": StringUtils.convert_enum_value(
                    builder.mobile_data.reference_number
                ),
                "sdk_trans_reference": StringUtils.convert_enum_value(
                    builder.mobile_data.sdk_trans_reference
                ),
            }

        # Add decoupled notification if present
        if (
            hasattr(builder, "decoupled_notification_url")
            and builder.decoupled_notification_url
        ):
            request_data["notifications"] = {
                "decoupled_notification_url": StringUtils.convert_enum_value(
                    builder.decoupled_notification_url
                ),
            }

        # Add decoupled flow request if present
        if (
            hasattr(builder, "decoupled_flow_request")
            and builder.decoupled_flow_request is not None
        ):
            request_data["decoupled_flow_request"] = StringUtils.convert_enum_value(
                DecoupledFlowRequest.DECOUPLED_PREFERRED
                if builder.decoupled_flow_request
                else DecoupledFlowRequest.DO_NOT_USE_DECOUPLED
            )

        # Add decoupled flow timeout if present
        if (
            hasattr(builder, "decoupled_flow_timeout")
            and builder.decoupled_flow_timeout
        ):
            request_data["decoupled_flow_timeout"] = StringUtils.convert_enum_value(
                builder.decoupled_flow_timeout
            )

        # Filter out None values
        request_data = self.filter_none_values(request_data)

        endpoint = GpApiRequest.AUTHENTICATIONS_ENDPOINT
        if (
            hasattr(builder, "three_d_secure")
            and builder.three_d_secure.server_transaction_id
        ):
            endpoint = (
                f"{endpoint}/{builder.three_d_secure.server_transaction_id}/initiate"
            )

        return GpApiRequest(endpoint, HttpVerb.POST, object_serialize(request_data))

    def build_verification_request(self, builder: Any, config: Any) -> GpApiRequest:
        """
        Builds a verification request

        Args:
            builder: The secure 3D builder
            config: The GP API configuration

        Returns:
            A GpApiRequest object
        """
        # Assuming there's a ThreeDSecure class in the Python SDK
        from globalpayments.api.entities import ThreeDSecure

        three_d_secure = builder.three_d_secure

        if not isinstance(three_d_secure, ThreeDSecure):
            raise ValueError("3D Secure data not found")

        endpoint = GpApiRequest.AUTHENTICATIONS_ENDPOINT
        if three_d_secure.server_transaction_id is not None:
            endpoint = f"{endpoint}/{three_d_secure.server_transaction_id}/result"

        return GpApiRequest(endpoint, HttpVerb.GET, "")

    def build_request_from_json(self, json_request: str, config: Any = None) -> Any:
        """
        Builds a request from a JSON string

        Args:
            json_request: The JSON string to build from
            config: The configuration to use

        Returns:
            The built request
        """
        # TODO: Implement this method
        pass

    def filter_none_values(self, data: Dict) -> Dict:
        """
        Recursively filters out None values from a dictionary

        Args:
            data: The dictionary to filter

        Returns:
            The filtered dictionary
        """
        if not isinstance(data, dict):
            return data

        result = {}
        for k, v in data.items():
            if v is None:
                continue

            if isinstance(v, dict):
                filtered = self.filter_none_values(v)
                if filtered:  # Only include non-empty dictionaries
                    result[k] = filtered
            else:
                result[k] = v

        return result

    def _set_payment_method_param(self, card_data: Any) -> Dict[str, Any]:
        """
        Sets payment method parameters based on the TypeScript implementation

        Args:
            card_data: The card data

        Returns:
            Payment method dictionary
        """
        payment_method = {}

        if hasattr(card_data, "token") and card_data.token:
            payment_method["id"] = StringUtils.convert_enum_value(card_data.token)

        if (
            hasattr(card_data, "is_card_data")
            and card_data.is_card_data
            and not (hasattr(card_data, "token") and card_data.token)
        ):
            exp_month = getattr(card_data, "exp_month", "") or ""
            exp_year = getattr(card_data, "exp_year", "")
            if exp_year:
                exp_year = str(exp_year).zfill(4)[
                    -2:
                ]  # Get last 2 digits, pad to 4 first
            else:
                exp_year = ""

            payment_method["card"] = {
                "brand": StringUtils.convert_enum_value(
                    getattr(card_data, "card_type", "").upper()
                    if hasattr(card_data, "card_type")
                    else ""
                ),
                "number": StringUtils.convert_enum_value(
                    getattr(card_data, "number", "") or ""
                ),
                "expiry_month": StringUtils.convert_enum_value(exp_month),
                "expiry_year": StringUtils.convert_enum_value(exp_year),
            }

            payment_method["name"] = StringUtils.convert_enum_value(
                getattr(card_data, "card_holder_name", "") or ""
            )

            # Mask sensitive values
            from globalpayments.api.utils.sensitive_data_utils import (
                ProtectSensitiveData,
            )

            self.masked_values.update(
                ProtectSensitiveData.hide_values(
                    {
                        "payment_method.card.expiry_month": exp_month,
                        "payment_method.card.expiry_year": exp_year,
                    }
                )
            )

            if hasattr(card_data, "number") and card_data.number:
                self.masked_values.update(
                    ProtectSensitiveData.hide_value(
                        "payment_method.card.number",
                        card_data.number,
                        4,
                        6,
                    )
                )

        return payment_method

    def _set_stored_credential_param(
        self, stored_credential: Any, request_data: Dict[str, Any]
    ) -> None:
        """
        Sets stored credential parameters based on the TypeScript implementation

        Args:
            stored_credential: The stored credential data
            request_data: The request data dictionary to modify
        """
        from globalpayments.api.utils.enum_mapping import EnumMapping
        from globalpayments.api.entities.enums import GatewayProvider

        if hasattr(stored_credential, "initiator"):
            initiator = EnumMapping.map_stored_credential_initiator(
                GatewayProvider.GpApi,
                stored_credential.initiator,
            )
            request_data["initiator"] = StringUtils.convert_enum_value(
                initiator if initiator else None
            )

        if (
            hasattr(stored_credential, "type")
            and hasattr(stored_credential, "reason")
            and hasattr(stored_credential, "sequence")
        ):
            request_data["stored_credential"] = {
                "model": StringUtils.convert_enum_value(
                    stored_credential.type.upper() if stored_credential.type else ""
                ),
                "reason": StringUtils.convert_enum_value(
                    stored_credential.reason.upper() if stored_credential.reason else ""
                ),
                "sequence": StringUtils.convert_enum_value(
                    stored_credential.sequence.upper()
                    if stored_credential.sequence
                    else ""
                ),
            }
