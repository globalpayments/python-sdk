"""
Class for storing payment method summary information
"""

from datetime import datetime
from typing import Optional


class StoredPaymentMethodSummary:
    """
    Represents a summary of a stored payment method in the system.
    """

    def __init__(self):
        """
        Initialize a new StoredPaymentMethodSummary object with default empty values
        """
        self.payment_method_id: Optional[str] = None
        self.time_created: Optional[datetime] = None
        self.status: Optional[str] = None
        self.reference: Optional[str] = None
        self.card_holder_name: Optional[str] = None
        self.card_type: Optional[str] = None
        self.card_number_last_four: Optional[str] = None
        self.card_exp_month: Optional[int] = None
        self.card_exp_year: Optional[int] = None
