"""
Provides session management for Global Payments API
"""

import hashlib
import json
from datetime import datetime
from typing import List, Optional

from globalpayments.api.builders.request_builder.GpApi.AccessTokenRequest import (
    AccessTokenRequest,
)
from globalpayments.api.entities.enums import IntervalToExpire, HttpVerb
from globalpayments.api.entities.gp_api.gp_api_request import GpApiRequest


class GpApiSessionInfo:
    """
    Handles session information and authentication for the Global Payments API
    """

    @staticmethod
    def generate_secret(nonce: str, app_key: str) -> str:
        """
        Generates a secret for authentication

        Args:
            nonce: A unique value for the request
            app_key: The application key

        Returns:
            The generated secret
        """
        combined = nonce + app_key
        return hashlib.sha512(combined.encode()).hexdigest().lower()

    @staticmethod
    def generate_nonce() -> str:
        """
        Generates a nonce for authentication

        Returns:
            The generated nonce
        """
        base = datetime.now()
        return base.isoformat()

    @staticmethod
    def sign_in(
        app_id: str,
        app_key: str,
        seconds_to_expire: Optional[int] = None,
        interval_to_expire: Optional[IntervalToExpire] = None,
        permissions: Optional[List[str]] = None,
    ) -> GpApiRequest:
        """
        Signs in to the Global Payments API

        Args:
            app_id: The application ID
            app_key: The application key
            seconds_to_expire: Seconds until token expires
            interval_to_expire: Interval at which the token expires
            permissions: List of permissions requested

        Returns:
            A GpApiRequest for authentication
        """
        nonce = GpApiSessionInfo.generate_nonce()
        permissions = permissions

        request_body = AccessTokenRequest(
            app_id,
            nonce,
            GpApiSessionInfo.generate_secret(nonce, app_key),
            "client_credentials",
            seconds_to_expire,
            interval_to_expire,
            permissions,
        )

        return GpApiRequest(
            GpApiRequest.ACCESS_TOKEN_ENDPOINT,
            HttpVerb.POST,
            json.dumps(request_body.gen_body()),
        )
