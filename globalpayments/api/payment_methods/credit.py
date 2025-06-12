"""
Credit payment method types
"""

import re
from dataclasses import dataclass, field
from typing import Optional, Any, Union

import globalpayments as gp
from globalpayments.api.entities.encryption_data import EncryptionData
from globalpayments.api.entities.enums import (
    CvnPresenceIndicator,
    EntryMethod,
    PaymentMethodType,
    TransactionType,
    TrackNumber,
    InquiryType,
)
from globalpayments.api.entities.three_d_secure import ThreeDSecure


@dataclass
class Credit(object):
    """
    Use credit as a payment method.
    """

    tokenizable: bool = field(default=True)

    encryption_data: Optional[EncryptionData] = field(default=None)
    """
    The card's encryption data; where applicable.
    """

    payment_method_type: PaymentMethodType = field(default=PaymentMethodType.Credit)
    """
    Set to L{PaymentMethodType.Credit} for internal methods.
    """

    three_d_secure: Optional[ThreeDSecure] = field(default=None)
    """
    3DSecure data attached to the card
    """

    token: Optional[str] = field(default=None)
    """
    A token value representing the card.
    """

    @property
    def is_card_data(self) -> bool:
        """
        Helper method to test if a L{Credit} object is card data.
        """
        try:
            _number_attr = getattr(self, "number")
            return True
        except AttributeError as _exc:
            return False

    @property
    def is_secure_3d(self) -> bool:
        """
        Helper method to test if a L{Credit} object is card data.
        """
        return True

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

    def balance_inquiry(
        self, inquiry: Optional[InquiryType] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        """
        Completes a balance inquiry (lookup) on the payment method.

        @type inquiry: L{BalanceInquiryType}
        @param inquiry: The type of inquiry to make
        @rtype: L{AuthorizationBuilder}
        @return: The builder
        """

        res = gp.api.builders.AuthorizationBuilder(TransactionType.Balance, self)
        if inquiry is not None:
            return res.with_balance_inquiry_type(inquiry)
        else:
            return res

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

    def tokenize(self, verify=True) -> "gp.api.builders.AuthorizationBuilder":
        """
        Tokenizes the payment method, verifying the payment method
        with the issuer in the process.

        @rtype: string
        @return: The requested token or None if tokenization fails
        """
        if verify:
            return self.verify().with_request_multi_use_token(True)
        else:
            return gp.api.builders.AuthorizationBuilder(TransactionType.Tokenize, self)

    def verify(self) -> "gp.api.builders.AuthorizationBuilder":
        """
        Verifies the payment method with the issuer.

        @rtype: L{AuthorizationBuilder}
        @return: The builder
        """

        return gp.api.builders.AuthorizationBuilder(TransactionType.Verify, self)

    def update_token_expiry(self) -> Any:
        """
        Updates expiration date contained within a Multi-Use Token

        @rtype: L{ManagementBuilder}
        @return: The builder
        """

        return gp.api.builders.ManagementBuilder(
            TransactionType.TokenUpdate, self
        ).execute()

    def update_token(self) -> "gp.api.builders.ManagementBuilder":
        """
        Updates expiration date contained within a Multi-Use Token

        @rtype: L{ManagementBuilder}
        @return: The builder
        """

        return gp.api.builders.ManagementBuilder(TransactionType.TokenUpdate, self)

    def delete_token(self) -> Any:
        """
        Deletes a Multi-Use Token from the gateway

        @rtype: L{ManagementBuilder}
        @return: The builder
        """

        return gp.api.builders.ManagementBuilder(
            TransactionType.TokenDelete, self
        ).execute()


@dataclass
class CreditCardData(Credit):
    """
    Use credit tokens or manual entry data as a payment method.
    """

    _cvn: Optional[str] = field(default=None)
    _number: Optional[str] = field(default=None)
    _regexDict: dict[str, str] = field(
        default_factory=lambda: {
            "Amex": r"^3[47][0-9]{13}$",
            "MC": r"^5[1-5][0-9]{14}$",
            "Visa": r"^4[0-9]{12}(?:[0-9]{3})?$",
            "DinersClub": r"^3(?:0[0-5]|[68][0-9])[0-9]{11}$",
            "EnRoute": r"^(2014|2149)",
            "Discover": r"^6(?:011|5[0-9]{2})[0-9]{12}$",
            "Jcb": r"^(?:2131|1800|35\d{3})\d{11}$",
        }
    )

    card_type: str = field(default="Unknown")
    """
    The card type of the manual entry data.

    Default value is `Unknown`.
    """

    card_present: bool = field(default=False)
    """
    Indicates if the card is present with the merchant at time of payment.

    Default value is `False`.
    """

    card_holder_name: Optional[str] = field(default=None)
    """
    The name on the front of the card.
    """

    cvn_presence_indicator: CvnPresenceIndicator = field(
        default=CvnPresenceIndicator.NotRequested
    )
    """
    Indicates card verification number (CVN) presence.

    Default value is L{CvnPresenceIndicator.NotRequested}.
    """

    exp_month: Optional[str] = field(default=None)
    """
    The card's expiration month.
    """

    exp_year: Optional[str] = field(default=None)
    """
    The card's expiration year.
    """

    reader_present: bool = field(default=False)
    """
    Indicates if a card reader was used when accepting the card data.

    Default value is `False`.
    """

    @property
    def cvn(self) -> Optional[str]:
        """
        The card's card verification number (CVN).

        When set, L{CreditCardData.cvn_presence_indicator} is set to
        L{CvnPresenceIndicator.Present}.
        """

        return self._cvn

    @cvn.setter
    def cvn(self, value: Optional[str]) -> None:
        if value is not None and value != "":
            self._cvn = value
            self.cvn_presence_indicator = CvnPresenceIndicator.Present

    @property
    def number(self) -> Optional[str]:
        """
        The card's number.
        """

        return self._number

    @number.setter
    def number(self, value: Optional[str]) -> None:
        if value is None:
            return

        self._number = value.replace(" ", "").replace("-", "")

        for name in self._regexDict:
            if re.match(self._regexDict[name], self._number) is not None:
                self.card_type = name
                break

    @property
    def short_expiry(self) -> str:
        """
        The card's expiration date in `MMYY` format.
        """

        month = str(self.exp_month).zfill(2)
        year = str(self.exp_year).zfill(4)[2:]
        return "{}{}".format(month, year)


@dataclass
class CreditTrackData(Credit):
    """
    Use credit track data as a payment method.
    """

    entry_method: Optional["EntryMethod"] = field(default=None)
    """
    Indicates how the card's track data was obtained.
    """

    value: Optional[str] = field(default=None)
    """
    The card's track data.
    """

    discretionary_data: Optional[str] = field(default=None)
    """
    The discretionary data from the card track.
    """

    encrypted_pan: Optional[str] = field(default=None)
    """
    Encrypted primary account number.
    """

    expiry: Optional[str] = field(default=None)
    """
    The expiration date of the card.
    """

    pan: Optional[str] = field(default=None)
    """
    Primary account number.
    """

    pin_block: Optional[str] = field(default=None)
    """
    The PIN block data.
    """

    purchase_device_sequence_number: Optional[str] = field(default=None)
    """
    Device sequence number used for purchase.
    """

    track_number: Optional[TrackNumber] = field(default=None)
    """
    Indicates which track was read from the card.
    """

    track_data: Optional[str] = field(default=None)
    """
    Raw track data from the card.
    """

    tokenization_data: Optional[str] = field(default=None)
    """
    Tokenized card data.
    """
