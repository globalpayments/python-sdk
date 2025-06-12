from typing import Optional, Union, Any
from dataclasses import dataclass, field
import globalpayments as gp
from globalpayments.api.entities.enums import (
    AliasAction,
    PaymentMethodType,
    TransactionType,
)
from globalpayments.api.entities.exceptions import ApiException
from globalpayments.api.entities.encryption_data import EncryptionData


@dataclass
class GiftCard(object):
    payment_method_type: PaymentMethodType = field(default=PaymentMethodType.Gift)
    pin: Optional[str] = field(default=None)
    value_type: Optional[str] = field(default=None)
    value: Optional[str] = field(default=None)

    # Additional attributes needed for type checking
    pin_block: Optional[str] = field(default=None)
    encryption_data: Optional[EncryptionData] = field(default=None)
    tokenizable: bool = field(default=False)

    @property
    def alias(self) -> Optional[str]:
        return self.value

    @alias.setter
    def alias(self, value: str) -> None:
        self.value = value
        self.value_type = "Alias"

    @property
    def number(self) -> Optional[str]:
        return self.value

    @number.setter
    def number(self, value: str) -> None:
        self.value = value
        self.value_type = "CardNbr"

    @property
    def token(self) -> Optional[str]:
        return self.value

    @token.setter
    def token(self, value: str) -> None:
        self.value = value
        self.value_type = "TokenValue"

    @property
    def track_data(self) -> Optional[str]:
        return self.value

    @track_data.setter
    def track_data(self, value: str) -> None:
        self.value = value
        self.value_type = "TrackData"

    @staticmethod
    def create(alias: Optional[str] = None, config_name: str = "default") -> "GiftCard":
        card = GiftCard()

        try:
            builder = gp.api.builders.AuthorizationBuilder(TransactionType.Alias, card)
            # Ensure alias is not None before passing it
            alias_value = alias if alias is not None else ""
            response = builder.with_alias(AliasAction.Create, alias_value).execute(
                config_name
            )

            if response is not None and response.response_code == "00":
                if response.gift_card is not None:
                    return response.gift_card
                raise ApiException("Gift card is null in the response")

            if response is not None and response.response_message is not None:
                raise ApiException(response.response_message)
            else:
                raise ApiException("Unknown error occurred during gift card creation")
        except Exception as e:
            raise ApiException(f"Unable to create gift card alias: {str(e)}")

    def add_alias(
        self, alias: Optional[str] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Alias, self)
        if alias is not None:
            builder = builder.with_alias(AliasAction.Add, alias)
        return builder

    def activate(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Activate, self)
        if amount is not None:
            builder = builder.with_amount(amount)
        return builder

    def add_value(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.AddValue, self)
        if amount is not None:
            builder = builder.with_amount(amount)
        return builder

    def balance_inquiry(
        self, inquiry: Optional[Any] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Balance, self)
        if inquiry is not None:
            builder = builder.with_balance_inquiry_type(inquiry)
        return builder

    def charge(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Sale, self)
        if amount is not None:
            builder = builder.with_amount(amount)
        return builder

    def deactivate(self) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        return AuthorizationBuilder(TransactionType.Deactivate, self)

    def remove_alias(
        self, alias: Optional[str] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Alias, self)
        if alias is not None:
            builder = builder.with_alias(AliasAction.Delete, alias)
        return builder

    def replace_with(
        self, new_card: Optional["GiftCard"] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Replace, self)
        if new_card is not None:
            builder = builder.with_replacement_card(new_card)
        return builder

    def reverse(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Reversal, self)
        if amount is not None:
            builder = builder.with_amount(amount)
        return builder

    def rewards(
        self, amount: Optional[Union[float, int, str]] = None
    ) -> "gp.api.builders.AuthorizationBuilder":
        from globalpayments.api.builders import AuthorizationBuilder

        builder = AuthorizationBuilder(TransactionType.Reward, self)
        if amount is not None:
            builder = builder.with_amount(amount)
        return builder
