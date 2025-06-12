from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class HostedPaymentData(object):
    """
    Data collection to supplement a hosted payment page.
    """

    customer_exists: Optional[bool] = field(default=None)
    customer_key: Optional[str] = field(default=None)
    customer_number: Optional[str] = field(default=None)
    offer_to_save_card: Optional[bool] = field(default=None)
    payment_key: Optional[str] = field(default=None)
    product_id: Optional[str] = field(default=None)
    supplementary_data: Dict[str, Any] = field(default_factory=dict)
