# -*- coding: utf-8 -*-

from typing import Dict, Optional, Any

from globalpayments.api.entities.enums import HttpVerb
from globalpayments.api.entities.request import Request


class GpApiRequest(Request):
    """
    Represents a request to the Global Payments API.
    Contains constants for various API endpoints.
    """

    # API endpoints
    ACCESS_TOKEN_ENDPOINT = "/accesstoken"
    TRANSACTION_ENDPOINT = "/transactions"
    PAYMENT_METHODS_ENDPOINT = "/payment-methods"
    VERIFICATIONS_ENDPOINT = "/verifications"
    DEPOSITS_ENDPOINT = "/settlement/deposits"
    DISPUTES_ENDPOINT = "/disputes"
    SETTLEMENT_DISPUTES_ENDPOINT = "/settlement/disputes"
    SETTLEMENT_TRANSACTIONS_ENDPOINT = "/settlement/transactions"
    AUTHENTICATIONS_ENDPOINT = "/authentications"
    BATCHES_ENDPOINT = "/batches"
    ACTIONS_ENDPOINT = "/actions"
    MERCHANT_MANAGEMENT_ENDPOINT = "/merchants"
    DCC_ENDPOINT = "/currency-conversions"
    PAYBYLINK_ENDPOINT = "/links"
    RISK_ASSESSMENTS = "/risk-assessments"
    ACCOUNTS_ENDPOINT = "/accounts"
    TRANSFER_ENDPOINT = "/transfers"
    DEVICE_ENDPOINT = "/devices"

    def __init__(
        self,
        endpoint: str,
        http_verb: HttpVerb,
        request_body: str = "",
        query_params: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new GpApiRequest object

        Args:
            endpoint: The API endpoint URL
            http_verb: The HTTP method (GET, POST, etc.)
            request_body: The request body content
            query_params: Query string parameters
        """
        super().__init__(endpoint, http_verb.value, request_body, query_params)
