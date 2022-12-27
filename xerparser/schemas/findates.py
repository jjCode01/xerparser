# xerparser
# findates.py

from datetime import datetime
from pydantic import BaseModel, Field


class FINDATES(BaseModel):
    """A class representing a Financial Period"""

    uid: str = Field(alias="fin_dates_id")  # Unique ID
    name: str = Field(alias="fin_dates_name")  # Period Name
    start_date: datetime
    end_date: datetime

    def __eq__(self, __o: "FINDATES") -> bool:
        return all(
            (
                self.name == __o.name,
                self.start_date == __o.start_date,
                self.end_date == __o.end_date,
            )
        )

    def __hash__(self) -> int:
        return hash((self.name, self.start_date, self.end_date))
