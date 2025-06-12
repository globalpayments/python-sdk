"""
Class for storing dispute document information
"""

from typing import Optional
from dataclasses import dataclass, field

from globalpayments.api.entities.document import Document


@dataclass
class DisputeDocument(Document):
    """
    Represents a document provided for a dispute case.
    """

    document_id: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None)
    b64_content: Optional[str] = field(default=None)
