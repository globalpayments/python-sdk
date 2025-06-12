from dataclasses import dataclass, field
from typing import Optional

from globalpayments.api.entities.enums import (
    StoredCredentialType,
    StoredCredentialInitiator,
    StoredCredentialSequence,
    StoredCredentialReason,
)


@dataclass
class StoredCredential:
    type: Optional[StoredCredentialType] = field(default=None)
    initiator: Optional[StoredCredentialInitiator] = field(
        default=None
    )  # This enum hasn't been defined yet
    sequence: Optional[StoredCredentialSequence] = field(default=None)
    schemeId: Optional[str] = field(default=None)
    reason: Optional[StoredCredentialReason] = field(default=None)
    cardBrandTransactionId: Optional[str] = field(default=None)
