# -*- coding: utf-8 -*-

from typing import Optional, List, Any


class PagedResult:
    """
    Represents a paged result from the Global Payments API.
    """

    def __init__(self):
        self.total_record_count: Optional[int] = None
        self.page_size: Optional[int] = None
        self.page: Optional[int] = None
        self.order: Optional[str] = None
        self.order_by: Optional[str] = None
        self.result: List[Any] = []
