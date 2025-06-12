# -*- coding: utf-8 -*-

from typing import Optional, Any, List, Dict

from globalpayments.api.entities.enums import PaymentEntryMode, PaymentMethodUsageMode
from .card import Card


class PaymentMethod:
    """
    Represents a payment method in the Global Payments API.
    """

    PAYMENT_METHOD_TOKEN_PREFIX = "PMT_"

    def __init__(self):
        self.id: Optional[str] = None
        self.entry_mode: Optional[PaymentEntryMode] = None
        self.authentication: Optional[Dict[str, Any]] = None
        self.encryption: Optional[Dict[str, Any]] = None
        self.name: Optional[str] = None
        self.storage_mode: Optional[PaymentMethodUsageMode] = None
        self.card: Optional[Card] = None
        self.digital_wallet: Optional[Dict[str, Any]] = None
        self.bank_transfer: Optional[Dict[str, Any]] = None
        self.apm: List[Dict[str, Any]] = []
        self.bnpl: Optional[Dict[str, Any]] = None
