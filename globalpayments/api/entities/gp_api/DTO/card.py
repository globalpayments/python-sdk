# -*- coding: utf-8 -*-

from typing import Optional


class Card:
    """
    Represents card data in the Global Payments API.
    """

    def __init__(self):
        self.number: Optional[str] = None
        self.expiry_month: Optional[str] = None
        self.expiry_year: Optional[str] = None
        self.cvv: Optional[str] = None
        self.cvv_indicator: Optional[str] = None
        self.avs_address: Optional[str] = None
        self.avs_postal_code: Optional[str] = None
        self.track: Optional[str] = None
        self.tag: Optional[str] = None
        self.funding: Optional[str] = None
        self.chip_condition: Optional[str] = None
        self.pin_block: Optional[str] = None
        self.brand_reference: Optional[str] = None
        self.authcode: Optional[str] = None
