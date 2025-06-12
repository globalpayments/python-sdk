# -*- coding: utf-8 -*-

import json
from typing import Optional, List, Dict, Any

from globalpayments.api.entities.gp_api.gp_api_account import GpApiAccount


class GpApiTokenResponse:
    """
    Represents a token response from the Global Payments API.
    """

    DATA_ACCOUNT_NAME_PREFIX = "DAA_"
    DISPUTE_MANAGEMENT_ACCOUNT_NAME_PREFIX = "DIA_"
    TOKENIZATION_ACCOUNT_NAME_PREFIX = "TKA_"
    TRANSACTION_PROCESSING_ACCOUNT_NAME_PREFIX = "TRA_"
    RIKS_ASSESSMENT_ACCOUNT_NAME_PREFIX = "RAA_"
    MERCHANT_MANAGEMENT_ACCOUNT_PREFIX = "MMA_"

    def __init__(self, response: str):
        self.token: Optional[str] = None
        self.type: Optional[str] = None
        self.time_created: Optional[str] = None
        self.seconds_to_expire: Optional[int] = None
        self.app_id: Optional[str] = None
        self.app_name: Optional[str] = None
        self.email: Optional[str] = None
        self.merchant_id: Optional[str] = None
        self.merchant_name: Optional[str] = None
        self.accounts: List[GpApiAccount] = []
        self.data_account_name: Optional[str] = None
        self.dispute_management_account_name: Optional[str] = None
        self.tokenization_account_name: Optional[str] = None
        self.transaction_processing_account_name: Optional[str] = None
        self.merchant_management_account_name: Optional[str] = None
        self.merchant_management_account_id: Optional[str] = None

        self.map_response_values(json.loads(response))

    def get_account_name(self, account_prefix: str) -> str:
        """
        Get account name for the given account prefix.

        Args:
            account_prefix: Account prefix to search for

        Returns:
            Account name if found, empty string otherwise
        """
        for account in self.accounts:
            if account.id and account.id[0:4] == account_prefix:
                return account.name if account.name is not None else ""

        return ""

    def get_account_id(self, account_prefix: str) -> str:
        """
        Get account ID for the given account prefix.

        Args:
            account_prefix: Account prefix to search for

        Returns:
            Account ID if found, empty string otherwise
        """
        for account in self.accounts:
            if account.id and account.id[0:4] == account_prefix:
                return account.id

        return ""

    def get_data_account_name(self) -> str:
        """Get data account name."""
        return self.get_account_name(self.DATA_ACCOUNT_NAME_PREFIX)

    def get_data_account_id(self) -> str:
        """Get data account ID."""
        return self.get_account_id(self.DATA_ACCOUNT_NAME_PREFIX)

    def get_dispute_management_account_name(self) -> str:
        """Get dispute management account name."""
        return self.get_account_name(self.DISPUTE_MANAGEMENT_ACCOUNT_NAME_PREFIX)

    def get_dispute_management_account_id(self) -> str:
        """Get dispute management account ID."""
        return self.get_account_id(self.DISPUTE_MANAGEMENT_ACCOUNT_NAME_PREFIX)

    def get_tokenization_account_name(self) -> str:
        """Get tokenization account name."""
        return self.get_account_name(self.TOKENIZATION_ACCOUNT_NAME_PREFIX)

    def get_tokenization_account_id(self) -> str:
        """Get tokenization account ID."""
        return self.get_account_id(self.TOKENIZATION_ACCOUNT_NAME_PREFIX)

    def get_transaction_processing_account_name(self) -> str:
        """Get transaction processing account name."""
        return self.get_account_name(self.TRANSACTION_PROCESSING_ACCOUNT_NAME_PREFIX)

    def get_transaction_processing_account_id(self) -> str:
        """Get transaction processing account ID."""
        return self.get_account_id(self.TRANSACTION_PROCESSING_ACCOUNT_NAME_PREFIX)

    def get_risk_assessment_account_name(self) -> str:
        """Get risk assessment account name."""
        return self.get_account_name(self.RIKS_ASSESSMENT_ACCOUNT_NAME_PREFIX)

    def get_risk_assessment_account_id(self) -> str:
        """Get risk assessment account ID."""
        return self.get_account_id(self.RIKS_ASSESSMENT_ACCOUNT_NAME_PREFIX)

    def get_merchant_management_account_name(self) -> str:
        """Get merchant management account name."""
        return self.get_account_name(self.MERCHANT_MANAGEMENT_ACCOUNT_PREFIX)

    def get_merchant_management_account_id(self) -> str:
        """Get merchant management account ID."""
        return self.get_account_id(self.MERCHANT_MANAGEMENT_ACCOUNT_PREFIX)

    def get_token(self) -> Optional[str]:
        """Get the token."""
        return self.token

    def map_response_values(self, response: Dict[str, Any]) -> None:
        """
        Map API response values to object properties.

        Args:
            response: API response dictionary
        """
        self.token = response.get("token")
        self.type = response.get("type")
        self.app_id = response.get("app_id")
        self.app_name = response.get("app_name")
        self.time_created = response.get("time_created")
        self.seconds_to_expire = response.get("seconds_to_expire")
        self.email = response.get("email")

        if "scope" in response:
            scope = response.get("scope", {})
            self.merchant_id = scope.get("merchant_id")
            self.merchant_name = scope.get("merchant_name")

            for account in scope.get("accounts", []):
                self.accounts.append(
                    GpApiAccount(account.get("id"), account.get("name"))
                )
