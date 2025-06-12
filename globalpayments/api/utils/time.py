from datetime import datetime
from typing import Union

import dateparser

from globalpayments.api.entities.enums import DateFormat


def format_time(d: Union[datetime, str, int], format: DateFormat) -> str:
    t = d
    if isinstance(d, int):
        t = dateparser.parse(str(t))
    if isinstance(d, str):
        t = dateparser.parse(t)
    return t.strftime(format.value)
