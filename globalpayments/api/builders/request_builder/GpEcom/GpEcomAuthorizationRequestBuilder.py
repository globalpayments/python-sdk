"""
Authorization request builder for Global Payments Ecommerce
"""

import xml.etree.ElementTree as ET
from typing import Any

from globalpayments.api.builders.request_builder.GpEcom.GpEcomRequestBuilder import (
    GpEcomRequestBuilder,
)
from globalpayments.api.builders.request_builder.IRequestBuilder import IRequestBuilder
from globalpayments.api.entities.enums import TransactionType
from globalpayments.api.utils import GenerationUtils


class GpEcomAuthorizationRequestBuilder(GpEcomRequestBuilder, IRequestBuilder):
    """
    Builds authorization requests for the Global Payments Ecommerce gateway
    """

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

        if not isinstance(builder, AuthorizationBuilder):
            return False

        transaction_type = builder.transaction_type

        payment_method = builder.payment_method
        if not payment_method:
            return False

        # Check if the payment method supports the transaction type
        if transaction_type != TransactionType.Verify:
            if not hasattr(payment_method, "supported_transaction_types"):
                return False

            transaction_types = payment_method.supported_transaction_types
            if transaction_type not in transaction_types:
                return False

        # This payment method doesn't require token for the request
        if (
            hasattr(payment_method, "token")
            and payment_method.token
            and builder.request_multi_use_token
        ):
            return False

        return True

    def build_request(self, builder: Any, config: Any) -> ET.Element:
        """
        Builds a request from the provided builder

        Args:
            builder: The authorization builder
            config: The GP Ecom configuration

        Returns:
            An XML element containing the request
        """
        # Create the request element based on transaction type
        transaction_type = builder.transaction_type

        # Define the root element and transaction type
        request = ET.Element(
            "request", {"timestamp": GenerationUtils.generate_timestamp(), "type": ""}
        )

        # Set the transaction type attribute
        if transaction_type == TransactionType.Auth:
            request.set("type", "auth")
        elif transaction_type == TransactionType.Sale:
            request.set("type", "payment")
        elif transaction_type == TransactionType.Verify:
            request.set("type", "validate")
        else:
            raise ValueError(f"Unknown transaction type: {transaction_type}")

        # Add merchant ID
        merchant_id = ET.SubElement(request, "merchantid")
        merchant_id.text = config.merchant_id

        # Add account
        if hasattr(config, "account") and config.account:
            account = ET.SubElement(request, "account")
            account.text = config.account

        # Add order information
        order = ET.SubElement(request, "orderid")
        order.text = builder.order_id or GenerationUtils.generate_order_id()

        # Add payment method
        amount = request
        if transaction_type != TransactionType.Verify:
            amount = ET.SubElement(request, "amount", {"currency": builder.currency})
            amount.text = self.number_format(builder.amount)

        # Add payment method details
        payment_method = builder.payment_method
        payment_data = ""

        # Handle different payment method types
        if hasattr(payment_method, "card_type") and payment_method.card_type:
            card = ET.SubElement(request, "card")

            number = ET.SubElement(card, "number")
            number.text = payment_method.number

            expiry_date = ET.SubElement(card, "expdate")
            expiry_date.text = f"{payment_method.exp_month}{payment_method.exp_year}"

            card_type = ET.SubElement(card, "type")
            card_type.text = payment_method.card_type

            card_holder_name = ET.SubElement(card, "chname")
            card_holder_name.text = payment_method.card_holder_name

            # For verification
            if transaction_type == TransactionType.Verify:
                payment_data = payment_method.number
            else:
                payment_data = payment_method.number

        # Add customer data if available
        if hasattr(builder, "customer_data") and builder.customer_data:
            customer_data = builder.customer_data
            payer = self.build_customer(customer_data)
            request.append(payer)

        # Add shipping data if available
        if hasattr(builder, "shipping_address") and builder.shipping_address:
            shipping = ET.Element("shipping")

            shipping_address = builder.shipping_address

            shipping_address_elem = ET.SubElement(shipping, "address")

            line1 = ET.SubElement(shipping_address_elem, "line1")
            line1.text = shipping_address.street_address1

            line2 = ET.SubElement(shipping_address_elem, "line2")
            line2.text = shipping_address.street_address2

            line3 = ET.SubElement(shipping_address_elem, "line3")
            line3.text = shipping_address.street_address3

            city = ET.SubElement(shipping_address_elem, "city")
            city.text = shipping_address.city

            postcode = ET.SubElement(shipping_address_elem, "postcode")
            postcode.text = shipping_address.postal_code

            country = ET.SubElement(
                shipping_address_elem,
                "country",
                {"code": shipping_address.country_code},
            )
            country.text = shipping_address.country

            request.append(shipping)

        # Add recurring data if available
        if hasattr(builder, "recurring_type") and builder.recurring_type:
            recurring = ET.SubElement(
                request, "recurring", {"type": builder.recurring_type}
            )

            if hasattr(builder, "recurring_sequence") and builder.recurring_sequence:
                recurring.set("sequence", builder.recurring_sequence)

        # Add supplementary data if available
        if hasattr(builder, "supplementary_data") and builder.supplementary_data:
            self.build_supplementary_data(builder.supplementary_data, request)

        # Add hash
        hash_element = ET.SubElement(request, "sha1hash")
        order_id = order.text if order and hasattr(order, "text") else ""
        amount_text = amount.text if amount and hasattr(amount, "text") else ""
        currency = (
            builder.currency
            if hasattr(builder, "currency") and builder.currency
            else ""
        )

        hash_value = self.generate_hash(
            config,
            request.get("timestamp", ""),
            order_id or "",
            amount_text or "" if transaction_type != TransactionType.Verify else "",
            currency if transaction_type != TransactionType.Verify else "",
            payment_data,
            transaction_type == TransactionType.Verify,
        )
        hash_element.text = hash_value

        return request

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
