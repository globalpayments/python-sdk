from typing import Optional, Union, Any
from dataclasses import dataclass, field
import globalpayments as gp
from globalpayments.api.entities.enums import (
    CvnPresenceIndicator,
    InquiryType,
    PaymentMethodType,
    TransactionType,
    EntryMethod,
)
from globalpayments.api.entities.encryption_data import EncryptionData


@dataclass
class EBT(object):
    payment_method_type: PaymentMethodType = field(default=PaymentMethodType.EBT)
    pin_block: Optional[str] = field(default=None)

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
        return gp.api.builders.AuthorizationBuilder(
            TransactionType.AddValue, self
        ).with_amount(amount)

    def balance_inquiry(
        self, inquiry: InquiryType = InquiryType.FoodStamp
    ) -> "gp.api.builders.AuthorizationBuilder":
        return (
            gp.api.builders.AuthorizationBuilder(TransactionType.Balance, self)
            .with_balance_inquiry_type(inquiry)
            .with_amount(0)
        )

    def benefit_withdrawal(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        return gp.api.builders.AuthorizationBuilder(
            TransactionType.BenefitWithdrawal, self
        ).with_amount(amount)

    def charge(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        return gp.api.builders.AuthorizationBuilder(
            TransactionType.Sale, self
        ).with_amount(amount)

    def refund(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        return gp.api.builders.AuthorizationBuilder(
            TransactionType.Refund, self
        ).with_amount(amount)

    def reverse(self, amount: Optional[Union[float, int, str]] = None) -> None:
        raise NotImplementedError()


@dataclass
class EBTCardData(EBT):
    approval_code: Optional[str] = field(default=None)
    number: Optional[str] = field(default=None)
    exp_month: Optional[str] = field(default=None)
    exp_year: Optional[str] = field(default=None)
    cvn: Optional[str] = field(default=None)
    cvn_presence_indicator: CvnPresenceIndicator = field(
        default=CvnPresenceIndicator.NotRequested
    )
    card_holder_name: Optional[str] = field(default=None)
    card_present: bool = field(default=False)
    reader_present: bool = field(default=False)
    serial_number: Optional[str] = field(default=None)


@dataclass
class EBTTrackData(EBT):
    encryption_data: Optional[EncryptionData] = field(default=None)
    entry_method: Optional[EntryMethod] = field(default=None)
    value: Optional[str] = field(default=None)
    serial_number: Optional[str] = field(default=None)
    approval_code: Optional[str] = field(default=None)
