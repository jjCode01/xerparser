# xerparser
# rsrc.py

from xerparser.schemas.rate import Rate
from xerparser.schemas.rsrc import RSRC


class RSRCRATE(Rate):
    def __init__(self, resource: RSRC, **data: str):
        super().__init__(**data)
        self.uid: str = data["rsrc_rate_id"]
        """(str) Unique Table ID"""
        self.rsrc_id: str = data["rsrc_id"]
        """(str) Resource Unique Table ID"""
        self.resource: RSRC = resource
        """(RSRC) Resource"""
        self.shift_period_id: str = data["shift_period_id"]
        """(str) Shift Unique Table ID"""
