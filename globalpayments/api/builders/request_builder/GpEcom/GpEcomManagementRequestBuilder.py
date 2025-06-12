"""
Management request builder for Global Payments Ecommerce
"""

import xml.etree.ElementTree as ET
from typing import Any

from globalpayments.api.builders.request_builder.GpEcom.GpEcomRequestBuilder import (
    GpEcomRequestBuilder,
)
from globalpayments.api.builders.request_builder.IRequestBuilder import IRequestBuilder
from globalpayments.api.entities.enums import TransactionType
from globalpayments.api.utils import GenerationUtils


class GpEcomManagementRequestBuilder(GpEcomRequestBuilder, IRequestBuilder):
    """
    Builds management requests for the Global Payments Ecommerce gateway
    """

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

    def build_request(self, builder: Any, config: Any) -> ET.Element:
        """
        Builds a request from the provided builder

        Args:
            builder: The management builder
            config: The GP Ecom configuration

        Returns:
            An XML element containing the request
        """
        # Create the request element based on transaction type
        transaction_type: TransactionType = builder.transaction_type

        # Define the root element and transaction type
        request = ET.Element(
            "request", {"timestamp": GenerationUtils.generate_timestamp(), "type": ""}
        )

        # Set the transaction type attribute
        if transaction_type == TransactionType.Capture:
            request.set("type", "settle")
        elif transaction_type == TransactionType.Hold:
            request.set("type", "hold")
        elif transaction_type == TransactionType.Refund:
            request.set("type", "rebate")
        elif transaction_type == TransactionType.Release:
            request.set("type", "release")
        elif transaction_type == TransactionType.Void:
            request.set("type", "void")
        else:
            raise ValueError(f"Unknown transaction type: {transaction_type}")

        # Add merchant ID
        merchant_id = ET.SubElement(request, "merchantid")
        merchant_id.text = config.merchant_id

        # Add account
        if hasattr(config, "account") and config.account:
            account = ET.SubElement(request, "account")
            account.text = config.account

        # Add channel
        if hasattr(config, "channel") and config.channel:
            channel = ET.SubElement(request, "channel")
            channel.text = config.channel

        # Add payment method
        payment_method = builder.payment_method

        # Add amount for transactions that need it
        amount = request
        if transaction_type in [TransactionType.Capture, TransactionType.Refund]:
            amount = ET.SubElement(request, "amount", {"currency": builder.currency})
            amount.text = self.number_format(builder.amount)

        # Add transaction ID for all transaction types
        if hasattr(payment_method, "transaction_id") and payment_method.transaction_id:
            pasref = ET.SubElement(request, "pasref")
            pasref.text = payment_method.transaction_id

        # Add authorization code for rebates
        if (
            transaction_type == TransactionType.Refund
            and hasattr(payment_method, "auth_code")
            and payment_method.auth_code
        ):
            auth_code = ET.SubElement(request, "authcode")
            auth_code.text = payment_method.auth_code

        # Add reason for transactions that need it
        if hasattr(builder, "description") and builder.description:
            comments = ET.SubElement(request, "comments")
            comment = ET.SubElement(comments, "comment", {"id": "1"})
            comment.text = builder.description

        # Add supplementary data if available
        if hasattr(builder, "supplementary_data") and builder.supplementary_data:
            self.build_supplementary_data(builder.supplementary_data, request)

        # Add order ID for refunds
        if (
            transaction_type == TransactionType.Refund
            and hasattr(builder, "order_id")
            and builder.order_id
        ):
            order_id = ET.SubElement(request, "orderid")
            order_id.text = builder.order_id

        # Add hash
        hash_element = ET.SubElement(request, "sha1hash")

        payment_data = ""
        if transaction_type == TransactionType.Refund:
            refund_hash = ""
            if hasattr(builder, "refund_password") and builder.refund_password:
                refund_hash = builder.refund_password
            else:
                refund_hash = config.refund_password

            payment_data = refund_hash

        transaction_id = (
            payment_method.transaction_id
            if payment_method and hasattr(payment_method, "transaction_id")
            else ""
        )
        amount_text = amount.text if amount and hasattr(amount, "text") else ""
        currency = builder.currency if builder.currency else ""

        hash_value = self.generate_hash(
            config,
            request.get("timestamp", ""),
            transaction_id,
            (
                amount_text or ""
                if transaction_type in [TransactionType.Capture, TransactionType.Refund]
                else ""
            ),
            (
                currency
                if transaction_type in [TransactionType.Capture, TransactionType.Refund]
                else ""
            ),
            payment_data,
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
