"""
Class for storing deposit summary information
"""

from datetime import datetime
from typing import Optional, Union

from .base_summary import BaseSummary


class DepositSummary(BaseSummary):
    """
    Represents a summary of a deposit transaction in the system.
    """

    def __init__(self):
        """
        Initialize a new DepositSummary object with default empty values
        """
        super().__init__()
        self.deposit_id: Optional[str] = None
        self.deposit_date: Optional[datetime] = None
        self.reference: Optional[str] = None
        self.type: Optional[str] = None
        self.routing_number: Optional[str] = None
        self.account_number: Optional[str] = None
        self.mode: Optional[str] = None
        self.summary_model: Optional[str] = None
        self.sales_total_count: Optional[int] = None
        self.sales_total_amount: Optional[str] = None
        self.sales_total_currency: Optional[str] = None
        self.refunds_total_count: Optional[int] = None
        self.refunds_total_amount: Optional[str] = None
        self.refunds_total_currency: Optional[str] = None
        self.chargeback_total_count: Optional[int] = None
        self.chargeback_total_amount: Optional[str] = None
        self.chargeback_total_currency: Optional[str] = None
        self.representment_total_count: Optional[int] = None
        self.representment_total_amount: Optional[Union[int, float]] = None
        self.representment_total_currency: Optional[str] = None
        self.fees_total_amount: Optional[str] = None
        self.fees_total_currency: Optional[str] = None
        self.adjustment_total_count: Optional[int] = None
        self.adjustment_total_amount: Optional[str] = None
        self.adjustment_total_currency: Optional[str] = None
        self.status: Optional[str] = None
