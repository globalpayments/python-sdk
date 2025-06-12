"""
Utilities for protecting sensitive data
"""

from typing import Dict, Union


class ProtectSensitiveData:
    """
    Utility class for masking and protecting sensitive data
    """

    @staticmethod
    def hide_value(
        field: str,
        value: str,
        visible_chars_at_start: int = 0,
        visible_chars_at_end: int = 0,
    ) -> Dict[str, str]:
        """
        Masks a sensitive value, showing only a specified number of characters
        at the beginning and end

        Args:
            field: The field name/key
            value: The value to mask
            visible_chars_at_start: Number of characters to show at the start
            visible_chars_at_end: Number of characters to show at the end

        Returns:
            A dictionary with the field name and masked value
        """
        if not value:
            return {}

        visible_chars_at_start = min(visible_chars_at_start, len(value))
        visible_chars_at_end = min(
            visible_chars_at_end, len(value) - visible_chars_at_start
        )

        if visible_chars_at_start + visible_chars_at_end >= len(value):
            return {field: value}

        masked_value = (
            value[:visible_chars_at_start]
            + "*" * (len(value) - visible_chars_at_start - visible_chars_at_end)
            + value[-visible_chars_at_end:]
            if visible_chars_at_end > 0
            else ""
        )

        return {field: masked_value}

    @staticmethod
    def hide_values(
        fields: Dict[str, str],
        visible_chars_at_start: int = 0,
        visible_chars_at_end: int = 0,
    ) -> Dict[str, str]:
        """
        Masks multiple sensitive values

        Args:
            fields: Dictionary of field names and values to mask
            visible_chars_at_start: Number of characters to show at the start
            visible_chars_at_end: Number of characters to show at the end

        Returns:
            A dictionary with field names and masked values
        """
        result = {}

        for field, value in fields.items():
            if value:
                result.update(
                    ProtectSensitiveData.hide_value(
                        field, value, visible_chars_at_start, visible_chars_at_end
                    )
                )

        return result
