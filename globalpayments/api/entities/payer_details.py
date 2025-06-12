"""
Payer details class for storing customer information
"""

from typing import Optional
from dataclasses import dataclass, field

from .address import Address


@dataclass
class PayerDetails:
    """
    Represents details about a customer/payer including personal and address information.
    """

    first_name: str = field(default="")
    last_name: str = field(default="")
    email: str = field(default="")
    billing_address: Optional[Address] = field(default=None)
    shipping_address: Optional[Address] = field(default=None)
