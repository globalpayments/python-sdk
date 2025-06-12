from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class TransactionSummary(object):
    """
    Transaction-level report data
    """

    amount: Optional[str] = field(default=None)
    convenience_amount: Optional[str] = field(default=None)
    shipping_amount: Optional[str] = field(default=None)
    auth_code: Optional[str] = field(default=None)
    authorized_amount: Optional[str] = field(default=None)
    client_transaction_id: Optional[str] = field(default=None)
    device_id: Optional[str] = field(default=None)
    issuer_response_code: Optional[str] = field(default=None)
    issuer_response_message: Optional[str] = field(default=None)
    masked_card_number: Optional[str] = field(default=None)
    original_transaction_id: Optional[str] = field(default=None)
    gateway_response_code: Optional[str] = field(default=None)
    gateway_response_message: Optional[str] = field(default=None)
    reference_number: Optional[str] = field(default=None)
    service_name: Optional[str] = field(default=None)
    settlement_amount: Optional[str] = field(default=None)
    status: Optional[str] = field(default=None)
    transaction_date: Optional[str] = field(default=None)
    transaction_id: Optional[str] = field(default=None)
    # Additional fields from gpapi_mapping.py
    payment_type: Optional[str] = field(default=None)
    account_number_last4: Optional[str] = field(default=None)
    account_type: Optional[str] = field(default=None)
    card_type: Optional[str] = field(default=None)
    brand_reference: Optional[str] = field(default=None)
    alternative_payment_response: Optional[Any] = field(default=None)
    transaction_status: Optional[str] = field(default=None)
    transaction_type: Optional[str] = field(default=None)
    channel: Optional[str] = field(default=None)
    currency: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    fingerprint: Optional[str] = field(default=None)
    fingerprint_indicator: Optional[str] = field(default=None)
    merchant_id: Optional[str] = field(default=None)
    merchant_hierarchy: Optional[str] = field(default=None)
    merchant_name: Optional[str] = field(default=None)
    merchant_dba_name: Optional[str] = field(default=None)
    aquirer_reference_number: Optional[str] = field(default=None)
    # Additional fields for GpApi compatibility
    transaction_local_date: Optional[str] = field(default=None)
    batch_sequence_number: Optional[str] = field(default=None)
    country: Optional[str] = field(default=None)
    deposit_reference: Optional[str] = field(default=None)
    deposit_status: Optional[str] = field(default=None)
    deposit_time_created: Optional[str] = field(default=None)
    order_id: Optional[str] = field(default=None)
    entry_mode: Optional[str] = field(default=None)
    card_holder_name: Optional[str] = field(default=None)
