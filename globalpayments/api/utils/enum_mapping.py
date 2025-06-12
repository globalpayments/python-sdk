"""
Utility for mapping enums between different systems
"""

from typing import Optional, List

from globalpayments.api import GatewayProvider
from globalpayments.api.entities.enums import (
    StoredCredentialInitiator,
    AccountType,
    SdkUiType,
    MessageCategory,
    EncyptedMobileType,
    CardType,
    EmvLastChipRead,
)


class EnumMapping:
    """
    Helper class to map between different enum representations.
    """

    @staticmethod
    def map_stored_credential_initiator(
        gateway_provider: GatewayProvider,
        initiator: Optional[StoredCredentialInitiator],
    ) -> str:
        """
        Maps the stored credential initiator value to the appropriate value
        for the specified gateway.

        Args:
            gateway_provider: The gateway provider
            initiator: The initiator value to map

        Returns:
            The mapped initiator value for the gateway
        """
        # Placeholder implementation, customize based on actual mapping needs
        if gateway_provider == GatewayProvider.GpApi:
            if initiator == StoredCredentialInitiator.Merchant:
                return "MERCHANT"
            elif initiator == StoredCredentialInitiator.CardHolder:
                return "PAYER"

        # Default: return the original value
        return initiator.value if initiator else ""

    @staticmethod
    def map_account_type(
        gateway: GatewayProvider,
        account_type: AccountType,
    ) -> Optional[str]:
        """
        Maps the account type to the appropriate value for the specified gateway.
        """
        if gateway == GatewayProvider.GpApi:
            if account_type == AccountType.Savings:
                return "SAVING"
            elif account_type == AccountType.Checking:
                return "CHECKING"
            elif account_type == AccountType.Credit:
                return "CREDIT"
            else:
                return None

        return account_type.value

    @staticmethod
    def map_digital_wallet_type(
        gateway: GatewayProvider,
        wallet_type: EncyptedMobileType,
    ) -> Optional[str]:
        """
        Maps the digital wallet type to the appropriate value for the specified gateway.
        """
        if gateway == GatewayProvider.GpApi:
            if wallet_type == EncyptedMobileType.ApplePay:
                return "APPLEPAY"
            elif wallet_type == EncyptedMobileType.GooglePay:
                return "PAY_BY_GOOGLE"
            elif wallet_type == EncyptedMobileType.ClickToPay:
                return "CLICK_TO_PAY"
            else:
                return None

        return None

    @staticmethod
    def map_emv_last_chip_read(
        gateway: GatewayProvider,
        value: EmvLastChipRead,
    ) -> Optional[str]:
        """
        Maps the EMV last chip read value to the appropriate value for the specified gateway.
        """
        if gateway == GatewayProvider.GpApi:
            if value == EmvLastChipRead.SUCCESSFUL:
                return "PREV_SUCCESS"
            elif value == EmvLastChipRead.FAILED:
                return "PREV_FAILED"

        return None

    @staticmethod
    def map_card_type(
        gateway: GatewayProvider,
        value: str,
    ) -> str:
        """
        Maps the card type to the appropriate value for the specified gateway.
        """
        if gateway in [GatewayProvider.GpEcom, GatewayProvider.GpApi]:
            if value == "DinersClub":
                return CardType.DINERS.value

        return value

    @staticmethod
    def map_sdk_ui_type(
        gateway: GatewayProvider,
        value: List[SdkUiType],
    ) -> List[str]:
        """
        Maps the SDK UI type to the appropriate value for the specified gateway.
        """
        if gateway == GatewayProvider.GpApi:
            # In Python, we need to check list contents differently
            if len(value) == 1 and value[0] == SdkUiType.Oob:
                return ["OUT_OF_BAND"]

        return [x.value for x in value]

    @staticmethod
    def map_message_category(
        gateway: GatewayProvider,
        value: MessageCategory,
    ) -> str:
        """
        Maps the message category to the appropriate value for the specified gateway.
        """
        if gateway == GatewayProvider.GpApi:
            if value == MessageCategory.PaymentAuthentication:
                return "PAYMENT"

        return value.value
