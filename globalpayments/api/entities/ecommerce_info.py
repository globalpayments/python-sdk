from datetime import datetime, timedelta
from globalpayments.api.entities.enums import ECommerceChannel


class ECommerceInfo(object):
    """
    ECommerce specific data to pass during authorization/settlement.
    """

    cavv = None
    channel = None
    eci = None
    payment_data_source = None
    payment_data_type = None
    ship_day = None
    ship_month = None
    xid = None

    def __init__(self):
        self.channel = ECommerceChannel.ECOM
        tomorrow = datetime.now() + timedelta(days=1)
        self.ship_day = tomorrow.day
        self.ship_month = tomorrow.month
        self.payment_data_type = '3DSecure'
