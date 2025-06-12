from dataclasses import dataclass, field
from typing import Optional

from globalpayments.api.entities.enums import ColorDepth, ChallengeWindowSize


@dataclass
class BrowserData:
    accept_header: Optional[str] = field(default=None)
    color_depth: Optional[ColorDepth] = field(default=None)
    ip_address: Optional[str] = field(default=None)
    java_enabled: Optional[bool] = field(default=None)
    java_script_enabled: Optional[bool] = field(default=None)
    language: Optional[str] = field(default=None)
    screen_height: Optional[int] = field(default=None)
    screen_width: Optional[int] = field(default=None)
    challenge_window_size: Optional[ChallengeWindowSize] = field(default=None)
    time_zone: Optional[str] = field(default=None)
    user_agent: Optional[str] = field(default=None)
