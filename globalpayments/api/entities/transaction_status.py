"""
Transaction status constants and mapping utilities.
"""

from typing import Dict


class TransactionStatus:
    """
    Constants for transaction status values.
    """

    INITIATED = "INITIATED"
    AUTHENTICATED = "AUTHENTICATED"
    PENDING = "PENDING"
    DECLINED = "DECLINED"
    PREAUTHORIZED = "PREAUTHORIZED"
    CAPTURED = "CAPTURED"
    BATCHED = "BATCHED"
    REVERSED = "REVERSED"
    FUNDED = "FUNDED"
    REJECTED = "REJECTED"

    # Mapping of transaction status to response values
    map_transaction_status_response: Dict[str, str] = {
        INITIATED: INITIATED,
        AUTHENTICATED: "SUCCESS_AUTHENTICATED",
        PENDING: PENDING,
        DECLINED: DECLINED,
        PREAUTHORIZED: PREAUTHORIZED,
        CAPTURED: CAPTURED,
        BATCHED: BATCHED,
        REVERSED: REVERSED,
        FUNDED: FUNDED,
        REJECTED: REJECTED,
    }
