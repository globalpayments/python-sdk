from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BatchSummary(object):
    """
    Details a closed batch.
    """

    id: Optional[str] = field(default=None)
    transaction_count: Optional[int] = field(default=None)
    total_amount: Optional[float] = field(default=None)
    sequence_number: Optional[str] = field(default=None)
