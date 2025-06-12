from typing import Optional, Union


class GatewayResponse(object):
    status_code: Optional[int] = None
    raw_response: Optional[Union[bytes, str]] = None
