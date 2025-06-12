"""
Credit payment method types
"""

from dataclasses import dataclass, field
from typing import Optional, Union

import globalpayments as gp
from globalpayments.api.entities.encryption_data import EncryptionData
from globalpayments.api.entities.enums import (
    PaymentMethodType,
    TransactionType,
)


@dataclass
class DebitTrackData(object):
    encryption_data: Optional[EncryptionData] = field(default=None)
    payment_method_type: PaymentMethodType = field(default=PaymentMethodType.Debit)
    pin_block: Optional[str] = field(default=None)
    value: Optional[str] = field(default=None)

    @property
    def is_track_data(self) -> bool:
        """
        Helper method to test if a L{Credit} object is track data.
        """
        try:
            _number_attr = getattr(self, "value")
            return True
        except AttributeError as _exc:
            return False

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

        return gp.api.builders.AuthorizationBuilder(
            TransactionType.Auth, self
        ).with_amount(amount)

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

        return gp.api.builders.AuthorizationBuilder(
            TransactionType.AddValue, self
        ).with_amount(amount)

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

        order_id: Optional[str] = None

        return gp.api.builders.AuthorizationBuilder(
            TransactionType.Sale, self
        ).with_amount(amount)

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

        return gp.api.builders.AuthorizationBuilder(
            TransactionType.Refund, self
        ).with_amount(amount)

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

        return gp.api.builders.AuthorizationBuilder(
            TransactionType.Reversal, self
        ).with_amount(amount)
