from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InstallmentData:
    """
    Represents installment payment plan data for a transaction.
    """

    # Indicates the installment payment plan program
    program: Optional[str] = field(default=None)

    # Indicates the mode of the installment plan chosen
    mode: Optional[str] = field(default=None)

    # Indicates the total number of payments to be made over the course of the installment payment plan
    count: Optional[str] = field(default=None)

    # Indicates the grace period before the first payment
    grace_period_count: Optional[str] = field(default=None)
