from datetime import datetime
from typing import Optional, Union
from dataclasses import dataclass, field

from globalpayments.api.entities.enums import DccProcessor, DccRateType


@dataclass
class DccRateData:
    """
    Data class for Dynamic Currency Conversion rate information
    """

    # The amount
    card_holder_amount: Optional[Union[float, str]] = field(default=None)

    # The currency
    card_holder_currency: Optional[str] = field(default=None)

    # The name of the CCP (Currency Conversion Processor) the request is to be sent to
    dcc_processor: Optional[DccProcessor] = field(default=None)

    # Rate Offered for the Exchange
    card_holder_rate: Optional[str] = field(default=None)

    # Rate type, 'S' for authorisation transactions (Sale). 'R' for Refunds.
    dcc_rate_type: Optional[DccRateType] = field(default=None)

    # The type of currency conversion rate obtained. Usually 1 but can contain other values.
    dcc_type: Optional[str] = field(default=None)

    # The orderId
    order_id: Optional[str] = field(default=None)

    # The DCC ID
    dcc_id: Optional[str] = field(default=None)

    # Commission Percentage
    commission_percentage: Optional[str] = field(default=None)

    # Exchange Rate Source Name
    exchange_rate_source_name: Optional[str] = field(default=None)

    # Exchange Rate Source Timestamp
    exchange_rate_source_timestamp: Optional[datetime] = field(default=None)

    # The merchant amount
    merchant_amount: Optional[Union[float, str]] = field(default=None)

    # The merchant currency
    merchant_currency: Optional[str] = field(default=None)

    # Margin Rate Percentage
    margin_rate_percentage: Optional[str] = field(default=None)
