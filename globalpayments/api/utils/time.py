from datetime import datetime
from typing import Optional, Union, cast

import dateparser

from globalpayments.api.entities.enums import DateFormat


def format_time(d: Union[datetime, str, int], format: DateFormat) -> str:
    t: Optional[datetime] = None
    if isinstance(d, datetime):
        t = d
    elif isinstance(d, (int, str)):
        t = dateparser.parse(str(d))
    assert t is not None
    return t.strftime(format.value)
