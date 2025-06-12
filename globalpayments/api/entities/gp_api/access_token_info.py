# -*- coding: utf-8 -*-

from typing import Optional


class AccessTokenInfo:
    """
    Stores information about a Global Payments API access token.
    """

    def __init__(self):
        self.access_token: Optional[str] = None
        self.merchant_id: Optional[str] = None
        self.data_account_name: Optional[str] = None
        self.dispute_management_account_name: Optional[str] = None
        self.tokenization_account_name: Optional[str] = None
        self.transaction_processing_account_name: Optional[str] = None
        self.risk_assessment_account_name: Optional[str] = None
        self.data_account_id: Optional[str] = None
        self.dispute_management_account_id: Optional[str] = None
        self.tokenization_account_id: Optional[str] = None
        self.transaction_processing_account_id: Optional[str] = None
        self.risk_assessment_account_id: Optional[str] = None
        self.merchant_management_account_name: Optional[str] = None
        self.merchant_management_account_id: Optional[str] = None
