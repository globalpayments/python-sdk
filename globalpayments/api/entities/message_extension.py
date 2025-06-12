"""
Class for message extension data in secure 3D transactions
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class MessageExtension:
    """
    Represents a message extension for 3D Secure transactions.
    """

    criticality_indicator: Optional[bool] = field(default=None)
    message_extension_data: Optional[str] = field(default=None)
    message_extension_id: Optional[str] = field(default=None)
    message_extension_name: Optional[str] = field(default=None)
