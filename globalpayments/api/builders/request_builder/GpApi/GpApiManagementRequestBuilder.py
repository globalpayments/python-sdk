"""
Management request builder for Global Payments API
"""

from typing import Any, Dict

from globalpayments.api.builders.request_builder.IRequestBuilder import IRequestBuilder
from globalpayments.api.entities.enums import (
    TransactionType,
    PaymentMethodType,
    HttpVerb,
)
from globalpayments.api.entities.gp_api.gp_api_request import GpApiRequest
from globalpayments.api.utils.serializer import object_serialize


class GpApiManagementRequestBuilder(IRequestBuilder):
    """
    Builds management requests for the Global Payments API
    """

    def __init__(self):
        """
        Initialize the management request builder
        """
        self.masked_values: Dict[str, str] = {}

    def can_process(self, builder: Any) -> bool:
        """
        Determines if this builder can process the provided builder

        Args:
            builder: The builder to check

        Returns:
            True if this builder can process the provided builder, otherwise False
        """
        # Assuming there's a ManagementBuilder class in the Python SDK
        from globalpayments.api.builders import ManagementBuilder

        return isinstance(builder, ManagementBuilder)

    def build_request(self, builder: Any, config: Any = None) -> GpApiRequest:
        """
        Builds a request from the provided builder

        Args:
            builder: The management builder
            config: The GP API configuration (not used in this implementation)

        Returns:
            A GpApiRequest object
        """
        payload = {}
        endpoint = ""
        verb = HttpVerb.POST  # Default to POST if not specified

        from globalpayments.api.payment_methods import CreditCardData
        from globalpayments.api.utils import StringUtils

        if builder.transaction_type == TransactionType.TokenDelete:
            token = (
                getattr(builder.payment_method, "token", "")
                if builder.payment_method
                else ""
            )
            endpoint = f"{GpApiRequest.PAYMENT_METHODS_ENDPOINT}/{token}"
            verb = HttpVerb.DELETE

        elif builder.transaction_type == TransactionType.TokenUpdate:
            if not isinstance(builder.payment_method, CreditCardData):
                raise ValueError("Payment method doesn't support this action!")

            token = getattr(builder.payment_method, "token", "")
            endpoint = f"{GpApiRequest.PAYMENT_METHODS_ENDPOINT}/{token}"
            verb = HttpVerb.PATCH

            # Assuming there's a Card class in the Python SDK
            from globalpayments.api.entities.gp_api.DTO.card import Card

            card = Card()
            builder_card = builder.payment_method

            exp_month = getattr(builder_card, "exp_month", None)
            card.expiry_month = str(exp_month) if exp_month else ""

            exp_year = getattr(builder_card, "exp_year", None)
            if exp_year:
                from globalpayments.api.utils import StringUtils

                exp_year = StringUtils.two_digit_year(str(exp_year))
                card.expiry_year = exp_year

            number = getattr(builder_card, "number", None)
            if number:
                card.number = number

            # Masking sensitive data - implement your ProtectSensitiveData class
            from globalpayments.api.utils.sensitive_data_utils import (
                ProtectSensitiveData,
            )

            if card.number is not None:
                self.masked_values.update(
                    ProtectSensitiveData.hide_value("card.number", card.number, 4, 6)
                )

            # Create a dictionary with non-None values only
            expiry_fields = {}
            if card.expiry_year is not None:
                expiry_fields["card.expiry_year"] = card.expiry_year
            if card.expiry_month is not None:
                expiry_fields["card.expiry_month"] = card.expiry_month

            if expiry_fields:
                self.masked_values.update(
                    ProtectSensitiveData.hide_values(expiry_fields)
                )

            payload = {
                "usage_mode": (
                    builder.payment_method_usage_mode
                    if hasattr(builder, "payment_method_usage_mode")
                    else None
                ),
                "name": (
                    builder_card.card_holder_name
                    if hasattr(builder_card, "card_holder_name")
                    else None
                ),
                "card": card.__dict__,
            }

        elif builder.transaction_type == TransactionType.Capture:
            transaction_id = getattr(builder.payment_method, "transaction_id", "")
            endpoint = f"{GpApiRequest.TRANSACTION_ENDPOINT}/{transaction_id}/capture"
            verb = HttpVerb.POST

            payload = {
                "amount": (
                    StringUtils.to_numeric(str(builder.amount))
                    if hasattr(builder, "amount") and builder.amount
                    else None
                ),
                "gratuity": (
                    StringUtils.to_numeric(str(builder.gratuity))
                    if hasattr(builder, "gratuity") and builder.gratuity
                    else None
                ),
                "currency_conversion": (
                    self.get_dcc_rate(builder.dcc_rate_data)
                    if hasattr(builder, "dcc_rate_data") and builder.dcc_rate_data
                    else None
                ),
            }

        elif builder.transaction_type == TransactionType.DisputeAcceptance:
            endpoint = (
                f"{GpApiRequest.DISPUTES_ENDPOINT}/{builder.dispute_id}/acceptance"
            )
            verb = HttpVerb.POST

        elif builder.transaction_type == TransactionType.DisputeChallenge:
            endpoint = (
                f"{GpApiRequest.DISPUTES_ENDPOINT}/{builder.dispute_id}/challenge"
            )
            verb = HttpVerb.POST

            payload = {"documents": builder.dispute_documents}

        elif builder.transaction_type == TransactionType.Refund:
            transaction_id = getattr(builder.payment_method, "transaction_id", "")
            endpoint = f"{GpApiRequest.TRANSACTION_ENDPOINT}/{transaction_id}/refund"
            verb = HttpVerb.POST

            payload = {
                "amount": (
                    StringUtils.to_numeric(str(builder.amount))
                    if hasattr(builder, "amount") and builder.amount
                    else None
                ),
                "currency_conversion": (
                    self.get_dcc_rate(builder.dcc_rate_data)
                    if hasattr(builder, "dcc_rate_data") and builder.dcc_rate_data
                    else None
                ),
            }

        elif builder.transaction_type == TransactionType.Reversal:
            transaction_id = getattr(builder.payment_method, "transaction_id", "")
            endpoint = f"{GpApiRequest.TRANSACTION_ENDPOINT}/{transaction_id}/reversal"

            payment_method_type = getattr(
                builder.payment_method, "payment_method_type", None
            )
            if payment_method_type == PaymentMethodType.AccountFunds:
                if hasattr(builder, "funds_data"):
                    merchant_id = getattr(builder.funds_data, "merchant_id", None)
                    if merchant_id:
                        endpoint = (
                            f"{GpApiRequest.MERCHANT_MANAGEMENT_ENDPOINT}/{merchant_id}"
                        )

            verb = HttpVerb.POST

            payload = {
                "amount": (
                    StringUtils.to_numeric(str(builder.amount))
                    if hasattr(builder, "amount") and builder.amount
                    else None
                ),
                "currency_conversion": (
                    self.get_dcc_rate(builder.dcc_rate_data)
                    if hasattr(builder, "dcc_rate_data") and builder.dcc_rate_data
                    else None
                ),
            }

        elif builder.transaction_type == TransactionType.Reauth:
            transaction_id = getattr(builder.payment_method, "transaction_id", "")
            endpoint = (
                f"{GpApiRequest.TRANSACTION_ENDPOINT}/{transaction_id}/reauthorization"
            )
            verb = HttpVerb.POST

            payload["amount"] = (
                StringUtils.to_numeric(str(builder.amount))
                if hasattr(builder, "amount") and builder.amount
                else None
            )

            payment_method_type = getattr(
                builder.payment_method, "payment_method_type", None
            )
            if payment_method_type == PaymentMethodType.ACH:
                payload["description"] = getattr(builder, "description", None)

        elif builder.transaction_type == TransactionType.Edit:
            transaction_id = getattr(builder.payment_method, "transaction_id", "")
            endpoint = (
                f"{GpApiRequest.TRANSACTION_ENDPOINT}/{transaction_id}/adjustment"
            )
            verb = HttpVerb.POST

            if hasattr(builder, "amount"):
                payload["amount"] = StringUtils.to_numeric(str(builder.amount))

            if hasattr(builder, "gratuity"):
                payload["gratuity_amount"] = StringUtils.to_numeric(
                    str(builder.gratuity)
                )

            if hasattr(builder, "tag_data") and builder.tag_data:
                payload["payment_method"] = {"card": {"tag": builder.tag_data}}

        elif builder.transaction_type == TransactionType.Auth:
            transaction_id = getattr(builder.payment_method, "transaction_id", "")
            endpoint = (
                f"{GpApiRequest.TRANSACTION_ENDPOINT}/{transaction_id}/incremental"
            )
            verb = HttpVerb.POST

            if hasattr(builder, "amount"):
                payload["amount"] = StringUtils.to_numeric(str(builder.amount))

            if hasattr(builder, "lodging_data") and builder.lodging_data:
                # Handle lodging data
                lodging = builder.lodging_data
                lodging_items = []

                if hasattr(lodging, "items") and lodging.items:
                    for item in lodging.items:
                        lodging_items.append(
                            {
                                "types": getattr(item, "types", None),
                                "reference": getattr(item, "reference", None),
                                "total_amount": (
                                    StringUtils.to_numeric(
                                        str(getattr(item, "total_amount", ""))
                                    )
                                    if hasattr(item, "total_amount")
                                    and getattr(item, "total_amount", None)
                                    else None
                                ),
                                "payment_method_program_codes": getattr(
                                    item, "payment_method_program_codes", None
                                ),
                            }
                        )

                payload["lodging"] = {
                    "booking_reference": getattr(lodging, "booking_reference", None),
                    "duration_days": getattr(lodging, "duration_days", None),
                    "date_checked_in": (
                        getattr(lodging, "checked_in_date", None).strftime("%Y-%m-%d")
                        if hasattr(lodging, "checked_in_date")
                        and getattr(lodging, "checked_in_date", None)
                        else None
                    ),
                    "date_checked_out": (
                        getattr(lodging, "checked_out_date", None).strftime("%Y-%m-%d")
                        if hasattr(lodging, "checked_out_date")
                        and getattr(lodging, "checked_out_date", None)
                        else None
                    ),
                    "daily_rate_amount": (
                        StringUtils.to_numeric(
                            str(getattr(lodging, "daily_rate_amount", ""))
                        )
                        if hasattr(lodging, "daily_rate_amount")
                        and getattr(lodging, "daily_rate_amount", None)
                        else None
                    ),
                    "lodging.charge_items": lodging_items or None,
                }

        elif builder.transaction_type == TransactionType.Confirm:
            from globalpayments.api.payment_methods import TransactionReference

            payment_method_type = getattr(
                builder.payment_method, "payment_method_type", None
            )
            if (
                isinstance(builder.payment_method, TransactionReference)
                and payment_method_type == PaymentMethodType.APM
            ):
                transaction_id = getattr(builder.payment_method, "transaction_id", "")
                endpoint = (
                    f"{GpApiRequest.TRANSACTION_ENDPOINT}/{transaction_id}/confirmation"
                )
                verb = HttpVerb.POST

                apm_response = getattr(
                    builder.payment_method, "alternative_payment_response", None
                )

                if apm_response:
                    provider_name = getattr(apm_response, "provider_name", None)
                    provider_reference = getattr(
                        apm_response, "provider_reference", None
                    )

                    payload = {
                        "payment_method": {
                            "apm": {
                                "provider": provider_name,
                                "provider_payer_reference": provider_reference,
                            }
                        }
                    }

        # Filter out None values
        if payload:
            payload = {k: v for k, v in payload.items() if v is not None}

        GpApiRequest.masked_values = self.masked_values

        return GpApiRequest(endpoint, verb, object_serialize(payload))

    def get_dcc_rate(self, dcc_rate_data: Any) -> Dict[str, str]:
        """
        Gets DCC rate information

        Args:
            dcc_rate_data: The DCC rate data

        Returns:
            A dictionary with DCC rate information
        """
        return {"id": dcc_rate_data.dcc_id}

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
