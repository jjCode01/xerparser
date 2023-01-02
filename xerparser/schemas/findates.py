# xerparser
# findates.py

from datetime import datetime
from xerparser.scripts.validators import date_format


class FINDATES:
    """A class representing a Financial Period"""

    def __init__(self, **data) -> None:
        self.uid: str = data["fin_dates_id"]  # Unique ID
        self.name: str = data["fin_dates_name"]  # Period Name
        self.start_date: datetime = datetime.strptime(data["start_date"], date_format)
        self.end_date: datetime = datetime.strptime(data["end_date"], date_format)

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
