"""
ACH/eCheck payment method types
"""

from dataclasses import dataclass, field
from typing import Optional, Union

import globalpayments as gp
from globalpayments.api.entities import Address
from globalpayments.api.entities.encryption_data import EncryptionData
from globalpayments.api.entities.enums import (
    PaymentMethodType,
    TransactionType,
    EntryMethod,
    AccountType,
    CheckType,
    SecCode,
)


@dataclass
class ECheck(object):
    """
    Use ACH/eCheck as a payment method.
    """

    account_number: Optional[str] = field(default=None)
    account_type: Optional[AccountType] = field(default=None)
    ach_verify: Optional[bool] = field(default=None)
    birth_year: Optional[str] = field(default=None)
    bank_address: Optional[Address] = field(default=None)
    check_holder_name: Optional[str] = field(default=None)
    check_name: Optional[str] = field(default=None)
    check_number: Optional[str] = field(default=None)
    check_type: Optional[CheckType] = field(default=None)
    check_verify: Optional[bool] = field(default=None)
    drivers_license_number: Optional[str] = field(default=None)
    drivers_license_state: Optional[str] = field(default=None)
    entry_mode: Optional[EntryMethod] = field(default=None)
    micr_number: Optional[str] = field(default=None)
    phone_number: Optional[str] = field(default=None)
    routing_number: Optional[str] = field(default=None)
    sec_code: Optional[SecCode] = field(default=None)
    ssn_last_4: Optional[str] = field(default=None)
    token: Optional[str] = field(default=None)

    payment_method_type: PaymentMethodType = field(default=PaymentMethodType.ACH)
    """
    Set to L{PaymentMethodType.ACH} for internal methods.
    """

    # Additional attributes needed for type checking
    pin_block: Optional[str] = field(default=None)
    encryption_data: Optional[EncryptionData] = field(default=None)
    tokenizable: bool = field(default=False)

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

        return gp.api.builders.AuthorizationBuilder(
            TransactionType.Sale, self
        ).with_amount(amount)
