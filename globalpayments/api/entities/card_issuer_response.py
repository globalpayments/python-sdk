"""
Card issuer response class for storing card issuer details
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class CardIssuerResponse:
    """
    Represents a response from a card issuer with validation results.
    """

    # The result code of the AVS check from the card issuer
    avs_result: Optional[str] = field(default=None)

    # Result code from the card issuer
    result: Optional[str] = field(default=None)

    # The result code of the CVV check from the card issuer
    cvv_result: Optional[str] = field(default=None)

    # The result code of the AVS address check from the card issuer
    avs_address_result: Optional[str] = field(default=None)

    # The result of the AVS postal code check from the card issuer
    avs_postal_code_result: Optional[str] = field(default=None)
