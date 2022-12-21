# xerparser
# findates.py

from datetime import datetime
from pydantic import BaseModel


class FINDATES(BaseModel):
    """A class representing a Financial Period"""

    fin_dates_id: str  # Unique ID
    fin_dates_name: str  # Period Name
    start_date: datetime
    end_date: datetime

    def __eq__(self, __o: "FINDATES") -> bool:
        return all(
            (
                self.fin_dates_name == __o.fin_dates_name,
                self.start_date == __o.start_date,
                self.end_date == __o.end_date,
            )
        )

    def __hash__(self) -> int:
        return hash((self.fin_dates_name, self.start_date, self.end_date))
