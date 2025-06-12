"""
Authorization request builder for Global Payments API
"""

from typing import Any, Dict, List, Optional

from globalpayments.api.builders.request_builder.IRequestBuilder import IRequestBuilder
from globalpayments.api.entities.enums import (
    GatewayProvider,
    TransactionType,
    TransactionModifier,
    HttpVerb,
)
from globalpayments.api.entities.gp_api.gp_api_request import GpApiRequest
from globalpayments.api.utils import GenerationUtils, StringUtils
from globalpayments.api.utils.serializer import object_serialize


class FraudManagement:
    """
    Represents fraud management settings
    """

    def __init__(self, mode: str, rules: Optional[List[Dict[str, str]]] = None):
        """
        Initialize fraud management settings

        Args:
            mode: The fraud filter mode
            rules: List of fraud rules
        """
        self.mode = mode
        self.rules = rules


class GpApiAuthorizationRequestBuilder(IRequestBuilder):
    """
    Builds authorization requests for the Global Payments API
    """

    def __init__(self):
        """
        Initialize the authorization request builder
        """
        self.builder = None
        self.masked_values: Dict[str, str] = {}

    def can_process(self, builder: Any) -> bool:
        """
        Determines if this builder can process the provided builder

        Args:
            builder: The builder to check

        Returns:
            True if this builder can process the provided builder, otherwise False
        """
        # Assuming there's an AuthorizationBuilder class in the Python SDK
        from globalpayments.api.builders import AuthorizationBuilder

        return isinstance(builder, AuthorizationBuilder)

    def build_request(self, builder: Any, config: Any) -> GpApiRequest:
        """
        Builds a request from the provided builder

        Args:
            builder: The authorization builder
            config: The GP API configuration

        Returns:
            A GpApiRequest object
        """
        self.builder = builder
        request_data = None
        endpoint = ""
        verb = HttpVerb.POST

        if (
            builder.transaction_type == TransactionType.Sale
            or builder.transaction_type == TransactionType.Refund
            or builder.transaction_type == TransactionType.Auth
        ):
            endpoint = GpApiRequest.TRANSACTION_ENDPOINT
            request_data = self.create_from_authorization_builder(builder, config)

        elif builder.transaction_type == TransactionType.Verify:
            if builder.request_multi_use_token and not getattr(
                builder.payment_method, "token", None
            ):
                endpoint = GpApiRequest.PAYMENT_METHODS_ENDPOINT
                expiry_year = None
                if getattr(builder.payment_method, "exp_year", None):
                    from globalpayments.api.utils import StringUtils

                    expiry_year = getattr(builder.payment_method, "exp_year", None)
                    expiry_year = StringUtils.two_digit_year(str(expiry_year))

                request_data = {
                    "account_name": config.access_token_info.tokenization_account_name,
                    "account_id": config.access_token_info.tokenization_account_id,
                    "name": builder.description,
                    "reference": builder.client_transaction_id
                    or GenerationUtils.generate_order_id(),
                    "usage_mode": builder.payment_method_usage_mode,
                    "fingerprint_mode": (
                        builder.customer_data.device_fingerprint
                        if builder.customer_data
                        else None
                    ),
                    "card": {
                        "number": getattr(builder.payment_method, "number", None),
                        "expiry_month": getattr(
                            builder.payment_method, "exp_month", None
                        ),
                        "expiry_year": expiry_year,
                        "cvv": getattr(builder.payment_method, "cvn", None),
                    },
                }

                # Filter out None values
                request_data = {k: v for k, v in request_data.items() if v is not None}

                from globalpayments.api.utils.sensitive_data_utils import (
                    ProtectSensitiveData,
                )

                # Create a dictionary with non-None values only
                card_fields = {}
                if request_data["card"].get("expiry_month") is not None:
                    card_fields["card.expiry_month"] = request_data["card"][
                        "expiry_month"
                    ]
                if request_data["card"].get("expiry_year") is not None:
                    card_fields["card.expiry_year"] = request_data["card"][
                        "expiry_year"
                    ]
                if request_data["card"].get("cvv") is not None:
                    card_fields["card.cvv"] = request_data["card"]["cvv"]

                if card_fields:
                    self.masked_values.update(
                        ProtectSensitiveData.hide_values(card_fields)
                    )

                self.masked_values.update(
                    ProtectSensitiveData.hide_value(
                        "card.number", request_data["card"]["number"], 4, 6
                    )
                )
            else:
                endpoint = GpApiRequest.VERIFICATIONS_ENDPOINT
                request_data = self.generate_verification_request(builder, config)

        elif builder.transaction_type == TransactionType.DccRateLookup:
            endpoint = GpApiRequest.DCC_ENDPOINT

            from globalpayments.api.utils import StringUtils

            request_data = {
                "account_name": config.access_token_info.transaction_processing_account_name,
                "account_id": config.access_token_info.transaction_processing_account_id,
                "channel": config.channel.value,
                "amount": StringUtils.to_numeric(
                    str(builder.amount) if builder.amount else None
                ),
                "currency": builder.currency,
                "country": config.country,
                "reference": builder.client_transaction_id
                or GenerationUtils.get_uuid(),
                "payment_method": self.create_payment_method_param(builder, config),
            }

            # Filter out None values
            request_data = {k: v for k, v in request_data.items() if v is not None}
        else:
            raise ValueError("Unsupported transaction type")

        GpApiRequest.masked_values = self.masked_values

        return GpApiRequest(endpoint, verb, object_serialize(request_data))

    def build_request_from_json(self, json_request: str, config: Any) -> Any:
        """
        Builds a request from a JSON string

        Args:
            json_request: The JSON string to build from
            config: The configuration to use

        Returns:
            The built request
        """
        # Per the TypeScript implementation, this is a placeholder for future implementation
        # This method is required by the IRequestBuilder interface but not yet implemented
        return None

    def generate_verification_request(
        self, builder: Any, config: Any
    ) -> Dict[str, Any]:
        """
        Generates a verification request

        Args:
            builder: The authorization builder
            config: The GP API configuration

        Returns:
            The verification request data
        """
        request_body = {
            "account_name": config.access_token_info.transaction_processing_account_name,
            "account_id": config.access_token_info.transaction_processing_account_id,
            "channel": config.channel.value,
            "reference": builder.client_transaction_id or GenerationUtils.get_uuid(),
            "currency": builder.currency,
            "country": config.country,
            "payment_method": self.create_payment_method_param(builder, config),
        }

        # Filter out None values
        request_body = {k: v for k, v in request_body.items() if v is not None}

        if getattr(builder, "stored_credential", False):
            self.set_request_stored_credentials(builder.stored_credential, request_body)

        return request_body

    def create_payment_method_param(self, builder: Any, config: Any) -> Dict[str, Any]:
        """
        Creates the payment method parameter

        Args:
            builder: The authorization builder
            config: The GP API configuration

        Returns:
            The payment method parameter
        """
        payment_method_container = builder.payment_method
        payment_method = {}

        payment_method["entry_mode"] = self.get_entry_mode(builder, config.channel)

        # Set name based on payment method type
        if hasattr(payment_method_container, "account_holder_name"):
            payment_method["name"] = getattr(
                payment_method_container, "account_holder_name", None
            )
        elif hasattr(payment_method_container, "card_holder_name"):
            payment_method["name"] = getattr(
                payment_method_container, "card_holder_name", None
            )

        payment_method["narrative"] = builder.dynamic_descriptor

        # Import necessary classes for type checking
        from globalpayments.api.payment_methods.credit import Credit
        from globalpayments.api.payment_methods.alternative_payment_method import (
            AlternativePaymentMethod,
        )

        # Handle different payment method types
        if isinstance(payment_method_container, Credit):
            if (
                hasattr(builder, "customer_data")
                and builder.customer_data
                and hasattr(builder.customer_data, "device_fingerprint")
            ):
                payment_method["fingerprint_mode"] = (
                    builder.customer_data.device_fingerprint
                )

            # Handle 3DS
            if hasattr(payment_method_container, "three_d_secure") and getattr(
                payment_method_container, "three_d_secure", None
            ):
                secure_ecom = getattr(payment_method_container, "three_d_secure", None)
                payment_method["authentication"] = {
                    "id": getattr(secure_ecom, "server_transaction_id", None),
                    "three_ds": {
                        "exempt_status": StringUtils.convert_enum_value(
                            getattr(secure_ecom, "exempt_status", None)
                        ),
                        "message_version": StringUtils.convert_enum_value(
                            getattr(secure_ecom, "message_version", None)
                        ),
                        "eci": getattr(secure_ecom, "eci", None),
                        "server_trans_reference": getattr(
                            secure_ecom, "server_transaction_id", None
                        ),
                        "ds_trans_reference": getattr(
                            secure_ecom, "directory_server_transaction_id", None
                        ),
                        "value": getattr(secure_ecom, "authentication_value", None),
                    },
                }
                # Filter out None values
                payment_method["authentication"]["three_ds"] = {
                    k: v
                    for k, v in payment_method["authentication"]["three_ds"].items()
                    if v is not None
                }

        # elif isinstance(payment_method_container, ECheck):
        #     payment_method["name"] = payment_method_container.check_holder_name
        #     payment_method["narrative"] = payment_method_container.merchant_notes
        #     payment_method["bank_transfer"] = {
        #         "account_number": payment_method_container.account_number,
        #         "account_type": EnumMapping.map_account_type(
        #             GatewayProvider.GpApi, payment_method_container.account_type
        #         ),
        #         "check_reference": payment_method_container.check_reference,
        #         "sec_code": payment_method_container.sec_code,
        #         "bank": {
        #             "code": payment_method_container.routing_number,
        #             "name": payment_method_container.bank_name,
        #             "address": {},
        #         },
        #     }
        #
        #     # Add bank address if available
        #     if (
        #         hasattr(payment_method_container, "bank_address")
        #         and payment_method_container.bank_address
        #     ):
        #         payment_method["bank_transfer"]["bank"]["address"] = {
        #             "line_1": payment_method_container.bank_address.street_address1,
        #             "line_2": payment_method_container.bank_address.street_address2,
        #             "line_3": payment_method_container.bank_address.street_address3,
        #             "city": payment_method_container.bank_address.city,
        #             "postal_code": payment_method_container.bank_address.postal_code,
        #             "state": payment_method_container.bank_address.state,
        #             "country": payment_method_container.bank_address.country_code,
        #         }
        #         # Filter out None values
        #         payment_method["bank_transfer"]["bank"]["address"] = {
        #             k: v
        #             for k, v in payment_method["bank_transfer"]["bank"][
        #                 "address"
        #             ].items()
        #             if v is not None
        #         }
        #
        #     # Mask sensitive data
        #     from globalpayments.api.utils.sensitive_data_utils import (
        #         ProtectSensitiveData,
        #     )
        #
        #     self.masked_values.update(
        #         ProtectSensitiveData.hide_values(
        #             {
        #                 "payment_method.bank_transfer.account_number": payment_method_container.account_number,
        #                 "payment_method.bank_transfer.bank.code": payment_method_container.routing_number,
        #             },
        #             4,
        #         )
        #     )
        #     return payment_method

        elif isinstance(payment_method_container, AlternativePaymentMethod):
            payment_method["apm"] = {
                "provider": getattr(
                    payment_method_container, "alternative_payment_method_type", None
                )
            }

            if hasattr(payment_method_container, "address_override_mode") and getattr(
                payment_method_container, "address_override_mode", None
            ):
                payment_method["apm"]["address_override_mode"] = getattr(
                    payment_method_container, "address_override_mode", None
                )

            return payment_method

        # Handle token or card data for non-mobile transactions
        if builder.transaction_modifier not in [
            TransactionModifier.EncryptedMobile,
            TransactionModifier.DecryptedMobile,
        ]:
            if hasattr(payment_method_container, "token") and getattr(
                payment_method_container, "token", None
            ):
                payment_method["id"] = getattr(payment_method_container, "token", None)

            if "id" not in payment_method:
                # Import CardUtils equivalent in Python
                from globalpayments.api.utils.card_utils import CardUtils

                payment_method["card"] = CardUtils.generate_card(
                    builder, GatewayProvider.GpApi, self.masked_values
                )
        else:
            # Handle digital wallet
            digital_wallet = {}

            if builder.transaction_modifier == TransactionModifier.EncryptedMobile:
                import json

                payment_token = None
                if (
                    hasattr(payment_method_container, "mobile_type")
                    and getattr(payment_method_container, "mobile_type", False)
                    == "CLICK_TO_PAY"
                ):
                    payment_token = {
                        "data": getattr(payment_method_container, "token", None)
                    }
                else:
                    if getattr(payment_method_container, "token", None):
                        # Replace double backslashes with single backslashes
                        token_str = getattr(
                            payment_method_container, "token", ""
                        ).replace("\\\\", "\\")
                        payment_token = json.loads(token_str)

                digital_wallet["payment_token"] = payment_token
            # if (
            #         hasattr(payment_method_container, "mobile_type")
            # ):
            #     digital_wallet["provider"] = EnumMapping.map_digital_wallet_type(
            #         GatewayProvider.GpApi,  getattr(payment_method_container, "mobile_type", '')
            #     )
            payment_method["digital_wallet"] = digital_wallet

        # Add card brand transaction ID if present
        if (
            hasattr(builder, "card_brand_transaction_id")
            and builder.card_brand_transaction_id
        ):
            if "card" not in payment_method:
                from globalpayments.api.entities.gp_api.DTO.card import Card

                payment_method["card"] = Card()

            payment_method["card"].brand_reference = builder.card_brand_transaction_id

        # Set storage mode if multi-use token is requested
        if builder.request_multi_use_token:
            payment_method["storage_mode"] = "ON_SUCCESS"

        # Filter out None values
        payment_method = {k: v for k, v in payment_method.items() if v is not None}

        return payment_method

    def create_from_authorization_builder(
        self, builder: Any, config: Any
    ) -> Dict[str, Any]:
        """
        Creates a request from an authorization builder

        Args:
            builder: The authorization builder
            config: The GP API configuration

        Returns:
            The authorization request data
        """
        from globalpayments.api.utils import StringUtils
        from globalpayments.api.payment_methods.credit import Credit

        capture_mode = self.get_capture_mode(builder)

        request_body = {
            "account_name": config.access_token_info.transaction_processing_account_name,
            "account_id": config.access_token_info.transaction_processing_account_id,
            "channel": config.channel.value,
            "country": config.country,
            "type": (
                "REFUND"
                if builder.transaction_type == TransactionType.Refund
                else "SALE"
            ),
            "capture_mode": capture_mode or "AUTO",
            "authorization_mode": "PARTIAL" if builder.allow_partial_auth else None,
            "amount": (
                StringUtils.to_numeric(str(builder.amount)) if builder.amount else None
            ),
            "currency": builder.currency,
            "reference": builder.client_transaction_id or GenerationUtils.get_uuid(),
        }

        # Add masked data response for ClickToPay
        if (
            isinstance(builder.payment_method, Credit)
            and hasattr(builder.payment_method, "mobile_type")
            and getattr(builder.payment_method, "mobile_type", None) == "CLICK_TO_PAY"
        ):
            request_body["masked"] = (
                "YES" if getattr(builder, "masked_data_response", False) else "NO"
            )

        # Add description if available
        request_body["description"] = (
            builder.description if hasattr(builder, "description") else None
        )

        # Add order reference if available
        if hasattr(builder, "order_id") and builder.order_id:
            request_body["order"] = {"reference": builder.order_id}

        # Add additional amounts
        if hasattr(builder, "gratuity") and builder.gratuity:
            request_body["gratuity_amount"] = StringUtils.to_numeric(
                str(builder.gratuity)
            )

        if hasattr(builder, "surcharge_amount") and builder.surcharge_amount:
            request_body["surcharge_amount"] = StringUtils.to_numeric(
                builder.surcharge_amount
            )

        if hasattr(builder, "convenience_amount") and builder.convenience_amount:
            request_body["convenience_amount"] = StringUtils.to_numeric(
                builder.convenience_amount
            )

        if hasattr(builder, "cash_back_amount") and builder.cash_back_amount:
            request_body["cashback_amount"] = StringUtils.to_numeric(
                str(builder.cash_back_amount)
            )

        # Add IP address and merchant category
        if hasattr(builder, "customer_ip_address"):
            request_body["ip_address"] = builder.customer_ip_address

        if hasattr(builder, "merchant_category"):
            request_body["merchant_category"] = builder.merchant_category

        # Add payment method
        request_body["payment_method"] = self.create_payment_method_param(
            builder, config
        )

        # Add fraud assessment if fraud filter is enabled
        if hasattr(builder, "fraud_filter") and builder.fraud_filter:
            request_body["risk_assessment"] = [self.map_fraud_management()]

        # Add payment link ID if available
        if hasattr(builder, "payment_link_id") and builder.payment_link_id:
            request_body["link"] = {"id": builder.payment_link_id}

        # Add payer information for ECheck or AlternativePaymentMethod
        from globalpayments.api.payment_methods.echeck import ECheck
        from globalpayments.api.payment_methods.alternative_payment_method import (
            AlternativePaymentMethod,
        )

        if isinstance(builder.payment_method, (ECheck, AlternativePaymentMethod)):
            payer_info = self.set_payer_information(builder)
            if payer_info:
                request_body["payer"] = payer_info

        # Handle Alternative Payment Method specific fields
        if isinstance(builder.payment_method, AlternativePaymentMethod):
            mapped_order = self.set_order_information(builder, request_body)
            notification_urls = self.set_notification_urls()

            # Update request body with mapped order and notification URLs
            if mapped_order:
                request_body["order"] = mapped_order

            if notification_urls:
                # Merge notification URLs into request body
                for key, value in notification_urls.items():
                    request_body[key] = value

            # Use order amount if available, otherwise use the builder amount
            if mapped_order and "amount" in mapped_order:
                request_body["amount"] = mapped_order["amount"]
            else:
                request_body["amount"] = (
                    StringUtils.to_numeric(str(builder.amount))
                    if builder.amount
                    else None
                )

        # Add DCC rate data if available
        if hasattr(builder, "dcc_rate_data") and builder.dcc_rate_data:
            request_body["currency_conversion"] = {"id": builder.dcc_rate_data.dcc_id}

        # Add stored credential information if available
        if hasattr(builder, "stored_credential") and builder.stored_credential:
            self.set_request_stored_credentials(builder.stored_credential, request_body)

        # Filter out None values
        request_body = {k: v for k, v in request_body.items() if v is not None}

        return request_body

    def set_notification_urls(self) -> Dict[str, Any]:
        """
        Sets notification URLs for the request

        Returns:
            A dictionary with notification URLs
        """
        return {
            "notifications": {
                "return_url": getattr(self.builder.payment_method, "return_url", None),
                "status_url": getattr(
                    self.builder.payment_method, "status_update_url", None
                ),
                "cancel_url": getattr(self.builder.payment_method, "cancel_url", None),
            }
        }

    def set_order_information(
        self, builder: Any, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Sets order information

        Args:
            builder: The authorization builder
            request: The current request

        Returns:
            The order information
        """
        order = {}

        if hasattr(builder, "order_details") and builder.order_details:
            order["description"] = builder.order_details.description

        # Add shipping address if available
        if hasattr(builder, "shipping_address") and builder.shipping_address:
            order["shipping_address"] = {
                "line_1": builder.shipping_address.street_address1,
                "line_2": builder.shipping_address.street_address2,
                "line_3": builder.shipping_address.street_address3,
                "city": builder.shipping_address.city,
                "postal_code": builder.shipping_address.postal_code,
                "state": builder.shipping_address.state,
                "country": builder.shipping_address.country,
            }

            # Filter out None values
            order["shipping_address"] = {
                k: v for k, v in order["shipping_address"].items() if v is not None
            }

        # Add shipping phone if available
        phone_number, phone_country_code = self.get_phone_number(builder, "SHIPPING")

        if phone_country_code or phone_number:
            order["shipping_phone"] = {
                "country_code": phone_country_code,
                "subscriber_number": phone_number,
            }

        # Handle alternative payment method specifics
        from globalpayments.api.payment_methods.alternative_payment_method import (
            AlternativePaymentMethod,
        )

        if isinstance(builder.payment_method, AlternativePaymentMethod):
            if hasattr(builder, "product_data") and builder.product_data:
                # Get item details for alternative payment methods
                order_details = self.set_item_details_list_for_apm(builder)
                if order_details:
                    # Merge with current order data
                    order.update(order_details)

        # Merge with existing order in request
        if "order" in request and request["order"]:
            order.update(request["order"])

        # Filter out None values
        order = {k: v for k, v in order.items() if v is not None}

        return order if order else {}

    def set_item_details_list_for_apm(self, builder: Any) -> Dict[str, Any]:
        """
        Sets item details for alternative payment methods

        Args:
            builder: The authorization builder

        Returns:
            The order with item details
        """
        from globalpayments.api.utils import StringUtils

        tax_total_amount = 0
        items_amount = 0
        order_amount = 0
        items = []
        order = {}

        # Process product data
        if hasattr(builder, "product_data") and builder.product_data:
            for product in builder.product_data:
                quantity = product.quantity or 0
                tax_amount = (
                    StringUtils.to_numeric(product.tax_amount)
                    if hasattr(product, "tax_amount")
                    else 0
                )
                unit_amount = (
                    StringUtils.to_numeric(product.unit_amount)
                    if hasattr(product, "unit_amount")
                    else 0
                )

                items.append(
                    {
                        "reference": (
                            product.reference if hasattr(product, "reference") else None
                        ),
                        "label": product.label if hasattr(product, "label") else None,
                        "description": (
                            product.description
                            if hasattr(product, "description")
                            else None
                        ),
                        "quantity": quantity,
                        "unit_amount": unit_amount,
                        "unit_currency": (
                            product.unit_currency
                            if hasattr(product, "unit_currency")
                            else None
                        ),
                        "tax_amount": tax_amount,
                        "amount": (
                            str(float(quantity) * float(unit_amount))
                            if quantity and unit_amount
                            else None
                        ),
                    }
                )

                # Filter out None values
                items[-1] = {k: v for k, v in items[-1].items() if v is not None}

                if hasattr(product, "tax_amount") and product.tax_amount:
                    tax_total_amount += float(product.tax_amount)

                if hasattr(product, "unit_amount") and product.unit_amount:
                    items_amount += float(product.quantity) * float(product.unit_amount)

        # Set order properties
        order["tax_amount"] = (
            StringUtils.to_numeric(str(tax_total_amount)) if tax_total_amount else None
        )
        order["item_amount"] = (
            StringUtils.to_numeric(str(items_amount)) if items_amount else None
        )

        if hasattr(builder, "shipping_amount") and builder.shipping_amount:
            order["shipping_amount"] = StringUtils.to_numeric(
                str(builder.shipping_amount)
            )
            order_amount += float(builder.shipping_amount)

        # Add shipping discount if available
        if hasattr(builder, "shipping_discount") and builder.shipping_discount:
            order["shipping_discount"] = StringUtils.to_numeric(
                builder.shipping_discount
            )

        # Add insurance information from order details
        if hasattr(builder, "order_details"):
            if (
                hasattr(builder.order_details, "has_insurance")
                and builder.order_details.has_insurance is not None
            ):
                order["insurance_offered"] = (
                    "YES" if builder.order_details.has_insurance else "NO"
                )

            # Add insurance amount if available
            if (
                hasattr(builder.order_details, "insurance_amount")
                and builder.order_details.insurance_amount
            ):
                order["insurance_amount"] = StringUtils.to_numeric(
                    str(builder.order_details.insurance_amount)
                )
                order_amount += float(builder.order_details.insurance_amount)

            # Add handling amount if available
            if (
                hasattr(builder.order_details, "handling_amount")
                and builder.order_details.handling_amount
            ):
                order["handling_amount"] = StringUtils.to_numeric(
                    str(builder.order_details.handling_amount)
                )
                order_amount += float(builder.order_details.handling_amount)

        # Calculate total order amount
        order_amount += items_amount + tax_total_amount
        order["amount"] = (
            StringUtils.to_numeric(str(order_amount)) if order_amount else None
        )
        order["currency"] = builder.currency
        order["items"] = items

        # Filter out None values
        order = {k: v for k, v in order.items() if v is not None}

        return order

    def set_request_stored_credentials(
        self, stored_credential: Any, request: Dict[str, Any]
    ) -> None:
        """
        Sets stored credential information in the request

        Args:
            stored_credential: The stored credential information
            request: The request to update
        """
        request["initiator"] = None

        if hasattr(stored_credential, "initiator") and stored_credential.initiator:
            # Use EnumMapping equivalent in Python
            from globalpayments.api.utils.enum_mapping import EnumMapping

            request["initiator"] = EnumMapping.map_stored_credential_initiator(
                GatewayProvider.GpApi, stored_credential.initiator
            )

        request["stored_credential"] = {
            "model": (
                stored_credential.type.upper()
                if hasattr(stored_credential, "type") and stored_credential.type
                else None
            ),
            "reason": (
                stored_credential.reason.upper()
                if hasattr(stored_credential, "reason") and stored_credential.reason
                else None
            ),
            "sequence": (
                stored_credential.sequence.upper()
                if hasattr(stored_credential, "sequence") and stored_credential.sequence
                else None
            ),
        }

        # Filter out None values
        request["stored_credential"] = {
            k: v for k, v in request["stored_credential"].items() if v is not None
        }

    def set_payer_information(self, builder: Any) -> Dict[str, Any]:
        """
        Sets payer information

        Args:
            builder: The authorization builder

        Returns:
            The payer information
        """
        from globalpayments.api.payment_methods.alternative_payment_method import (
            AlternativePaymentMethod,
        )
        from globalpayments.api.payment_methods.echeck import ECheck
        from globalpayments.api.utils import StringUtils

        payer = {}

        if hasattr(builder, "customer_id") and builder.customer_id:
            payer["id"] = builder.customer_id
        elif (
            hasattr(builder, "customer_data")
            and hasattr(builder.customer_data, "id")
            and builder.customer_data.id
        ):
            payer["id"] = builder.customer_data.id

        if hasattr(builder, "customer_data") and builder.customer_data:
            if hasattr(builder.customer_data, "key"):
                payer["reference"] = builder.customer_data.key

        # Add payment method specific information
        if isinstance(builder.payment_method, AlternativePaymentMethod):
            # Add home phone if available
            if (
                hasattr(builder, "home_phone")
                and builder.home_phone
                and (
                    hasattr(builder.home_phone, "country_code")
                    or hasattr(builder.home_phone, "number")
                )
            ):
                payer["home_phone"] = {}

                if hasattr(builder.home_phone, "country_code"):
                    payer["home_phone"]["country_code"] = (
                        StringUtils.validate_to_number(builder.home_phone.country_code)
                    )

                if hasattr(builder.home_phone, "number"):
                    payer["home_phone"]["subscriber_number"] = (
                        StringUtils.validate_to_number(builder.home_phone.number)
                    )

                # Remove empty dict if no phone details were added
                if not payer["home_phone"]:
                    del payer["home_phone"]

            # Add work phone if available
            if (
                hasattr(builder, "work_phone")
                and builder.work_phone
                and (
                    hasattr(builder.work_phone, "country_code")
                    or hasattr(builder.work_phone, "number")
                )
            ):
                payer["work_phone"] = {}

                if hasattr(builder.work_phone, "country_code"):
                    payer["work_phone"]["country_code"] = (
                        StringUtils.validate_to_number(builder.work_phone.country_code)
                    )

                if hasattr(builder.work_phone, "number"):
                    payer["work_phone"]["subscriber_number"] = (
                        StringUtils.validate_to_number(builder.work_phone.number)
                    )

                # Remove empty dict if no phone details were added
                if not payer["work_phone"]:
                    del payer["work_phone"]

        elif isinstance(builder.payment_method, ECheck):
            # Add billing address for ECheck
            if hasattr(builder, "billing_address") and builder.billing_address:
                payer["billing_address"] = {
                    "line_1": builder.billing_address.street_address1,
                    "line_2": builder.billing_address.street_address2,
                    "city": builder.billing_address.city,
                    "postal_code": builder.billing_address.postal_code,
                    "state": builder.billing_address.state,
                    "country": builder.billing_address.country_code,
                }

                # Filter out None values
                payer["billing_address"] = {
                    k: v for k, v in payer["billing_address"].items() if v is not None
                }

            # Add customer data
            if hasattr(builder, "customer_data") and builder.customer_data:
                if (
                    hasattr(builder.customer_data, "first_name")
                    and hasattr(builder.customer_data, "last_name")
                    and builder.customer_data.first_name
                    and builder.customer_data.last_name
                ):
                    payer["name"] = (
                        f"{builder.customer_data.first_name} {builder.customer_data.last_name}"
                    )

                if hasattr(builder.customer_data, "date_of_birth"):
                    payer["date_of_birth"] = builder.customer_data.date_of_birth

            # Add phone numbers
            home_phone = self.get_phone_number(builder, "HOME")
            if home_phone[0] or home_phone[1]:
                payer["landline_phone"] = home_phone[1] + home_phone[0]

            mobile_phone = self.get_phone_number(builder, "MOBILE")
            if mobile_phone[0] or mobile_phone[1]:
                payer["mobile_phone"] = mobile_phone[1] + mobile_phone[0]

        # Filter out None values
        payer = {k: v for k, v in payer.items() if v is not None}

        return payer if payer else {}

    def get_phone_number(self, builder: Any, phone_type: str) -> tuple:
        """
        Gets a phone number from the builder

        Args:
            builder: The authorization builder
            phone_type: The type of phone number to get

        Returns:
            A tuple of (phone_number, country_code)
        """
        from globalpayments.api.utils import StringUtils

        phone_key = phone_type.lower() + "_phone"
        phone_country_code = ""
        phone_number = ""

        if (
            hasattr(builder, "customer_data")
            and hasattr(builder.customer_data, phone_key)
            and builder.customer_data[phone_key]
        ):
            phone_country_code = builder.customer_data[phone_key].country_code
            phone_number = builder.customer_data[phone_key].number

        if (
            phone_number == ""
            and hasattr(builder, phone_key)
            and getattr(builder, phone_key)
        ):
            phone_country_code = getattr(builder, phone_key).country_code
            phone_number = getattr(builder, phone_key).number

        return (
            StringUtils.validate_to_number(phone_number),
            StringUtils.validate_to_number(phone_country_code),
        )

    def get_entry_mode(self, builder: Any, channel: Any) -> str:
        """
        Gets the entry mode for the payment

        Args:
            builder: The authorization builder
            channel: The channel (card present, card not present)

        Returns:
            The payment entry mode
        """

        from globalpayments.api import CardChannel

        if channel == CardChannel.CARD_PRESENT:
            # Logic for card present transactions
            if getattr(builder.payment_method, "is_track_data", False):
                if builder.tag_data:
                    if (
                        getattr(builder.payment_method, "entry_method", None)
                        == "Proximity"
                    ):
                        return "CONTACTLESS_CHIP"
                    return "CHIP"

                if getattr(builder.payment_method, "entry_method", None) == "SWIPE":
                    return "SWIPE"

            if getattr(builder.payment_method, "is_card_data", False) and getattr(
                builder.payment_method, "card_present", False
            ):
                return "MANUAL"

            return "SWIPE"

        elif channel == CardChannel.CARD_NOT_PRESENT:
            # Logic for card not present transactions
            if getattr(builder.payment_method, "is_card_data", False):
                if getattr(builder.payment_method, "reader_present", None) == True:
                    return "ECOM"

                if getattr(
                    builder.payment_method, "reader_present", None
                ) == False and hasattr(builder.payment_method, "entry_method"):
                    if getattr(builder.payment_method, "entry_method", None) == "PHONE":
                        return "PHONE"
                    elif (
                        getattr(builder.payment_method, "entry_method", None) == "MOTO"
                    ):
                        return "MOTO"
                    elif (
                        getattr(builder.payment_method, "entry_method", None) == "MAIL"
                    ):
                        return "MAIL"

                if (
                    builder.transaction_modifier == TransactionModifier.EncryptedMobile
                    and hasattr(builder.payment_method, "has_in_app_payment_data")
                    and callable(
                        getattr(builder.payment_method, "has_in_app_payment_data")
                    )
                    and builder.payment_method.has_in_app_payment_data()
                ):
                    return "IN_APP"

            return "ECOM"

        raise ValueError("Please configure the channel!")

    def get_capture_mode(self, builder: Any) -> str:
        """
        Gets the capture mode for the transaction

        Args:
            builder: The authorization builder

        Returns:
            The capture mode
        """
        if getattr(builder, "multi_capture", False):
            return "MULTIPLE"

        if builder.transaction_type == TransactionType.Auth:
            return "LATER"

        return "AUTO"

    def map_fraud_management(self) -> FraudManagement:
        """
        Maps fraud management settings

        Returns:
            The fraud management settings
        """
        rules = None

        if hasattr(self.builder, "fraud_rules") and self.builder.fraud_rules:
            rules = []
            for fraud_rule in self.builder.fraud_rules:
                rules.append({"reference": fraud_rule.key, "mode": fraud_rule.mode})

        return FraudManagement(mode=self.builder.fraud_filter, rules=rules)
