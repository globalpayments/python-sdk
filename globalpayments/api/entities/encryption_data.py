from typing import Optional, Union, Self
from dataclasses import dataclass, field


@dataclass
class EncryptionData(object):
    """
    Details how encrypted track data was encrypted by the device
    in order for the gateway to decrypt the data.
    """

    version: Optional[str] = field(default=None)
    track_number: Optional[str] = field(default=None)
    ksn: Optional[str] = field(default=None)
    ktb: Optional[str] = field(default=None)

    @staticmethod
    def version_1() -> "EncryptionData":
        rvalue = EncryptionData()
        rvalue.version = "01"
        return rvalue

    @staticmethod
    def version_2(ktb: str, track_number: Optional[str] = None) -> "EncryptionData":
        rvalue = EncryptionData()
        rvalue.version = "02"
        rvalue.ktb = ktb
        rvalue.track_number = track_number
        return rvalue
