"""
Card class for storing card details
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Card:
    """
    Represents payment card details.
    """

    cardholder_name: Optional[str] = field(default=None)

    card_number: Optional[str] = field(default=None)

    masked_card_number: Optional[str] = field(default=None)

    card_exp_month: Optional[str] = field(default=None)

    card_exp_year: Optional[str] = field(default=None)

    token: Optional[str] = field(default=None)

    # Masked card number with last 4 digits showing
    masked_number_last4: Optional[str] = field(default=None)

    # Indicates the card brand that issued the card
    brand: Optional[str] = field(default=None)

    # The unique reference created by the brands/schemes to uniquely identify the transaction
    brand_reference: Optional[str] = field(default=None)

    # Contains the first 6 digits of the card
    bin: Optional[str] = field(default=None)

    # The issuing country that the bin is associated with
    bin_country: Optional[str] = field(default=None)

    # The card provider's description of their card product
    account_type: Optional[str] = field(default=None)

    # The label of the issuing bank or financial institution of the bin
    issuer: Optional[str] = field(default=None)
