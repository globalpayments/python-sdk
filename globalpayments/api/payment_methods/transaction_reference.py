from typing import Optional, Any
from dataclasses import dataclass, field
from globalpayments.api.entities.enums import PaymentMethodType
from globalpayments.api.entities.encryption_data import EncryptionData


@dataclass
class TransactionReference(object):
    auth_code: Optional[str] = field(default=None)
    client_transaction_id: Optional[str] = field(default=None)
    order_id: Optional[str] = field(default=None)
    payment_method_type: Optional[PaymentMethodType] = field(default=None)
    transaction_id: Optional[str] = field(default=None)

    # Additional attributes needed for type checking
    pin_block: Optional[str] = field(default=None)
    encryption_data: Optional[EncryptionData] = field(default=None)
    tokenizable: bool = field(default=False)
    alternative_payment_response: Optional[Any] = field(default=None)
