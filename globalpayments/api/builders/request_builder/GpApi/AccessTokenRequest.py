"""
Class representing an access token request
"""

from typing import List, Optional

from globalpayments.api.entities.enums import IntervalToExpire


class AccessTokenRequest:
    """
    Represents a request for access token from the Global Payments API
    """

    def __init__(
        self,
        app_id: str,
        nonce: str,
        secret: str,
        grant_type: str,
        seconds_to_expire: Optional[int] = None,
        interval_to_expire: Optional[IntervalToExpire] = None,
        permissions: Optional[List[str]] = None,
    ):
        """
        Initialize access token request

        Args:
            app_id: The application ID
            nonce: A unique value for the request
            secret: The generated secret
            grant_type: The type of grant for authorization
            seconds_to_expire: Seconds until token expires
            interval_to_expire: Interval at which the token expires
            permissions: List of permissions requested
        """
        self.app_id = app_id
        self.nonce = nonce
        self.secret = secret
        self.grant_type = grant_type
        self.seconds_to_expire = seconds_to_expire if seconds_to_expire else None
        self.interval_to_expire = (
            interval_to_expire.value if interval_to_expire else None
        )
        self.permissions = permissions

    def gen_body(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}
