"""
Request class for API interactions
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Request:
    """
    Represents an API request with associated properties.
    """

    endpoint: str
    http_verb: str
    request_body: str = field(default="")
    query_params: Optional[Dict[str, Any]] = field(default=None)

    # Instance variable for storing masked values
    masked_values: Dict[str, str] = field(default_factory=dict)
