from dataclasses import dataclass, field
from typing import Optional, List

from globalpayments.api.entities.enums import SdkInterface, SdkUiType


@dataclass
class MobileData:
    encodedData: Optional[str] = field(default=None)
    applicationReference: Optional[str] = field(default=None)
    sdkInterface: Optional[SdkInterface] = field(default=None)
    sdkUiTypes: Optional[List[SdkUiType]] = field(default=None)
    ephemeralPublicKey: Optional[str] = field(default=None)
    maximumTimeout: Optional[int] = field(default=None)
    referenceNumber: Optional[str] = field(default=None)
    sdkTransReference: Optional[str] = field(default=None)
