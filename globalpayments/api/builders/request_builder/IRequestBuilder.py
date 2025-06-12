"""
Interface for request builders
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class IRequestBuilder(ABC):
    """
    Interface for request builders
    """

    @abstractmethod
    def can_process(self, builder: Any) -> bool:
        """
        Determines if this builder can process the provided builder

        Args:
            builder: The builder to check

        Returns:
            True if this builder can process the provided builder, otherwise False
        """
        pass

    @abstractmethod
    def build_request(self, builder: Any, config: Any) -> Any:
        """
        Builds a request from the provided builder

        Args:
            builder: The builder to build from
            config: The configuration to use

        Returns:
            The built request
        """
        pass

    @abstractmethod
    def build_request_from_json(self, json_request: str, config: Any) -> Any:
        """
        Builds a request from a JSON string

        Args:
            json_request: The JSON string to build from
            config: The configuration to use

        Returns:
            The built request
        """
        pass
