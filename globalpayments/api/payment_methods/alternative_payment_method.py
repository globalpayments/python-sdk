"""
Alternative payment method types
"""

from dataclasses import dataclass, field
from typing import Optional, Union

import globalpayments as gp
from globalpayments.api.entities import UnsupportedTransactionException
from globalpayments.api.entities.encryption_data import EncryptionData
from globalpayments.api.entities.enums import (
    PaymentMethodType,
    TransactionModifier,
    TransactionType,
)


@dataclass
class AlternativePaymentMethod:
    """
    Use alternative payment methods as a payment method.
    """

    alternative_payment_method_type: str
    """
    The type of alternative payment method.
    """

    payment_method_type: PaymentMethodType = field(default=PaymentMethodType.APM)
    """
    Set to L{PaymentMethodType.APM} for internal methods.
    """

    return_url: Optional[str] = field(default=None)
    """
    The URL to return to after processing.
    """

    status_update_url: Optional[str] = field(default=None)
    """
    The URL to receive status updates.
    """

    cancel_url: Optional[str] = field(default=None)
    """
    The URL to return to when the customer cancels the payment.
    """

    descriptor: Optional[str] = field(default=None)
    """
    The payment descriptor.
    """

    country: Optional[str] = field(default=None)
    """
    The country associated with the payment.
    """

    account_holder_name: Optional[str] = field(default=None)
    """
    The account holder name.
    """

    provider_reference: Optional[str] = field(default=None)
    """
    The provider reference for the alternative payment.
    """

    address_override_mode: Optional[str] = field(default=None)
    """
    The address override mode.
    """

    pin_block: Optional[str] = field(default=None)
    """
    The PIN block data.
    """

    encryption_data: Optional[EncryptionData] = field(default=None)
    """
    The encryption data for the payment.
    """

    def charge(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        """
        Creates a charge (sale) against the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        """
        return (
            gp.api.builders.AuthorizationBuilder(TransactionType.Sale, self)
            .with_transaction_modifier(TransactionModifier.AlternativePaymentMethod)
            .with_amount(amount)
        )

    def authorize(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        """
        Creates an authorization against the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        """
        return (
            gp.api.builders.AuthorizationBuilder(TransactionType.Auth, self)
            .with_transaction_modifier(TransactionModifier.AlternativePaymentMethod)
            .with_amount(amount)
        )

    def add_value(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        """
        Adds value to to a payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        """
        # Silence unused argument warning
        _ = amount
        raise UnsupportedTransactionException()

    def refund(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        """
        Refunds the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        """
        # Silence unused argument warning
        _ = amount
        raise UnsupportedTransactionException()

    def reverse(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        """
        Reverses a previous transaction against the payment method.

        @type amount: number
        @param amount: The amount of the transaction
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        """
        # Silence unused argument warning
        _ = amount
        raise UnsupportedTransactionException()
