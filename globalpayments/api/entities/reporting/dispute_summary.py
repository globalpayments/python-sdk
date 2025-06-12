"""
Class for storing dispute summary information
"""

from datetime import datetime
from typing import Optional, List, Union

from ...entities.dispute_document import DisputeDocument
from ...entities.enums import TransactionType


class DisputeSummary:
    """
    Represents a summary of a dispute in the system.
    """

    def __init__(self):
        """
        Initialize a new DisputeSummary object with default empty values
        """
        self.merchant_hierarchy: Optional[str] = None
        self.merchant_name: Optional[str] = None
        self.merchant_dba_name: Optional[str] = None
        self.merchant_number: Optional[str] = None
        self.merchant_category: Optional[str] = None
        self.deposit_date: Optional[datetime] = None
        self.deposit_reference: Optional[str] = None
        self.deposit_type: Optional[str] = None
        self.type: Optional[str] = None
        self.case_amount: Optional[str] = None
        self.case_currency: Optional[str] = None
        self.case_stage: Optional[str] = None
        self.case_status: Optional[str] = None
        self.case_description: Optional[str] = None
        self.transaction_order_id: Optional[str] = None
        self.transaction_local_time: Optional[datetime] = None
        self.transaction_time: Optional[datetime] = None
        self.transaction_type: Optional[str] = None
        self.transaction_amount: Optional[str] = None
        self.transaction_currency: Optional[str] = None
        self.case_number: Optional[str] = None
        self.case_time: Optional[datetime] = None
        self.case_id: Optional[str] = None
        self.case_id_time: Optional[Union[datetime, str]] = None
        self.case_merchant_id: Optional[str] = None
        self.case_terminal_id: Optional[str] = None
        self.transaction_arn: Optional[str] = None
        self.transaction_reference_number: Optional[str] = None
        self.transaction_srd: Optional[str] = None
        self.transaction_auth_code: Optional[str] = None
        self.transaction_card_type: Optional[str] = None
        self.transaction_masked_card_number: Optional[str] = None
        self.reason: Optional[str] = None
        self.reason_code: Optional[str] = None
        self.result: Optional[str] = None
        self.issuer_comment: Optional[str] = None
        self.issuer_case_number: Optional[str] = None
        self.dispute_amount: Optional[float] = None
        self.dispute_currency: Optional[str] = None
        self.dispute_customer_amount: Optional[float] = None
        self.dispute_customer_currency: Optional[str] = None
        self.respond_by_date: Optional[datetime] = None
        self.case_original_reference: Optional[str] = None
        self.last_adjustment_amount: Optional[str] = None
        self.last_adjustment_currency: Optional[str] = None
        self.last_adjustment_funding: Optional[str] = None
        self.documents: List[DisputeDocument] = []

    def accept(self) -> "ManagementBuilder":
        """
        Accept the dispute

        Returns:
            A ManagementBuilder configured for dispute acceptance
        """
        from ...builders import ManagementBuilder

        return ManagementBuilder(TransactionType.DisputeAcceptance).with_dispute_id(
            self.case_id or ""
        )

    def challenge(self, documents: List[DisputeDocument]) -> "ManagementBuilder":
        """
        Challenge the dispute with supporting documentation

        Args:
            documents: List of dispute documents to support the challenge

        Returns:
            A ManagementBuilder configured for dispute challenge
        """
        from ...builders import ManagementBuilder

        return (
            ManagementBuilder(TransactionType.DisputeChallenge)
            .with_dispute_id(self.case_id or "")
            .with_dispute_documents(documents)
        )
