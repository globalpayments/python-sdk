"""
Class for alternative payment response data
"""

from typing import Optional, Union
from dataclasses import dataclass, field


@dataclass
class AlternativePaymentResponse:
    """
    Represents a response from an alternative payment method provider.
    """

    # Bank account details
    bank_account: Optional[str] = field(default=None)

    # Account holder name of the customer's account
    account_holder_name: Optional[str] = field(default=None)

    # 2 character ISO country code
    country: Optional[str] = field(default=None)

    # URL to redirect the customer to - only available in PENDING asynchronous transactions.
    # Sent there so merchant can redirect consumer to complete an interrupted payment.
    redirect_url: Optional[Union[str, int]] = field(default=None)

    # This parameter reflects what the customer will see on the proof of payment
    # (for example, bank statement record and similar). Also known as the payment descriptor
    payment_purpose: Optional[str] = field(default=None)

    # The payment method used
    payment_method: Optional[str] = field(default=None)

    # The provider reference
    provider_reference: Optional[str] = field(default=None)

    # The APM provider name
    provider_name: Optional[str] = field(default=None)

    # Standard fields
    ack: Optional[str] = field(default=None)
    session_token: Optional[str] = field(default=None)
    correlation_reference: Optional[str] = field(default=None)
    version_reference: Optional[str] = field(default=None)
    build_reference: Optional[str] = field(default=None)
    time_created_reference: Optional[str] = field(default=None)
    transaction_reference: Optional[str] = field(default=None)
    secure_account_reference: Optional[str] = field(default=None)
    reason_code: Optional[str] = field(default=None)
    pending_reason: Optional[str] = field(default=None)
    gross_amount: Optional[str] = field(default=None)
    payment_time_reference: Optional[str] = field(default=None)
    payment_type: Optional[str] = field(default=None)
    payment_status: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None)
    protection_eligibilty: Optional[str] = field(default=None)

    # Authorization related fields
    auth_status: Optional[str] = field(default=None)
    auth_amount: Optional[str] = field(default=None)
    auth_ack: Optional[str] = field(default=None)
    auth_correlation_reference: Optional[str] = field(default=None)
    auth_version_reference: Optional[str] = field(default=None)
    auth_build_reference: Optional[str] = field(default=None)
    auth_pending_reason: Optional[str] = field(default=None)
    auth_protection_eligibilty: Optional[str] = field(default=None)
    auth_protection_eligibilty_type: Optional[str] = field(default=None)
    auth_reference: Optional[str] = field(default=None)
    fee_amount: Optional[str] = field(default=None)

    # Alipay specific fields
    next_action: Optional[str] = field(default=None)
    seconds_to_expire: Optional[str] = field(default=None)
    qr_code_image: Optional[str] = field(default=None)
