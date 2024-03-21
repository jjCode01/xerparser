# xerparser
# findates.py

from datetime import datetime

from xerparser.src.validators import date_format


class FINDATES:
    """
    A class representing a Financial Period
    """

    def __init__(self, **data: str) -> None:
        self.uid: str = data["fin_dates_id"]
        """Unique Table ID"""
        self.name: str = data["fin_dates_name"]
        """Financial Period Name"""
        self.start_date: datetime = datetime.strptime(data["start_date"], date_format)
        """Financial Period Start Date"""
        self.end_date: datetime = datetime.strptime(data["end_date"], date_format)
        """Financial Period End Date"""

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
