"""
Base document class for document submissions
"""

from typing import Optional
from dataclasses import dataclass, field

from globalpayments.api.entities.enums import FileType, DocumentCategory


@dataclass
class Document:
    """
    Represents a document in the Global Payments API.
    """

    id: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    status: Optional[str] = field(default=None)
    time_created: Optional[str] = field(default=None)
    format: Optional[FileType] = field(default=None)
    category: Optional[DocumentCategory] = field(default=None)
