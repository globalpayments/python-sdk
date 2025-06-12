# -*- coding: utf-8 -*-

from typing import Optional


class GpApiAccount:
    """
    Represents an account in the Global Payments API.
    """

    def __init__(self, id: Optional[str] = None, name: Optional[str] = None):
        self.id: Optional[str] = id
        self.name: Optional[str] = name
