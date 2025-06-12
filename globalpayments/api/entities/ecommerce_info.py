from datetime import datetime, timedelta
from typing import Optional, Union
from dataclasses import dataclass, field
from globalpayments.api.entities.enums import ECommerceChannel


@dataclass
class ECommerceInfo(object):
    """
    ECommerce specific data to pass during authorization/settlement.
    """

    cavv: Optional[str] = field(default=None)
    channel: Optional[ECommerceChannel] = field(default=None)
    eci: Optional[str] = field(default=None)
    payment_data_source: Optional[str] = field(default=None)
    payment_data_type: Optional[str] = field(default=None)
    ship_day: Optional[Union[int, str]] = field(default=None)
    ship_month: Optional[Union[int, str]] = field(default=None)
    xid: Optional[str] = field(default=None)

    def __init__(self):
        self.channel = ECommerceChannel.ECOM
        tomorrow = datetime.now() + timedelta(days=1)
        self.ship_day = tomorrow.day
        self.ship_month = tomorrow.month
        self.payment_data_type = "3DSecure"
