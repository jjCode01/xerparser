# xerparser
# findates.py

from datetime import datetime
from xerparser.src.validators import date_format


class FINDATES:
    """
    A class representing a Financial Period

    ...

    Attributes
    ----------
    uid: str
        Unique ID [fin_dates_id]
    name: str
        Financial Period Name [fin_dates_name]
    start_date: datetime
        Start Date of Financial Period
    end_date: datetime
        End Date of Financial Period
    """

    def __init__(self, **data) -> None:
        self.uid: str = data["fin_dates_id"]
        self.name: str = data["fin_dates_name"]
        self.start_date: datetime = datetime.strptime(data["start_date"], date_format)
        self.end_date: datetime = datetime.strptime(data["end_date"], date_format)

    def __eq__(self, __o: "FINDATES") -> bool:
        return self.start_date == __o.start_date and self.end_date == __o.end_date

    def __gt__(self, __o: "FINDATES") -> bool:
        if self.start_date == __o.start_date:
            return self.end_date > __o.end_date
        return self.start_date > __o.start_date

    def __lt__(self, __o: "FINDATES") -> bool:
        if self.start_date == __o.start_date:
            return self.end_date < __o.end_date
        return self.start_date < __o.start_date

    def __hash__(self) -> int:
        return hash((self.name, self.start_date, self.end_date))
