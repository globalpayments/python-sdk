"""
Base class for various summary objects in the reporting module
"""

from typing import Optional


class BaseSummary:
    """
    Abstract base class for summary objects that provides common properties
    """

    def __init__(self):
        """
        Initialize a new BaseSummary object with default empty values
        """
        self.amount: Optional[str] = None
        self.currency: Optional[str] = None
        self.merchant_id: Optional[str] = None
        self.merchant_hierarchy: Optional[str] = None
        self.merchant_name: Optional[str] = None
        self.merchant_dba_name: Optional[str] = None
