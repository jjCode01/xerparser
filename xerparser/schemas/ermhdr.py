# xerparser
# ermhdr.py

from datetime import datetime


class ERMHDR:
    """
    Export information for .xer file.

    Attributes
    ----------
    version: str
        Version of P6 set during export
    date: datetime
        Date .xer file was created
    user: str
        User name that created the .xer file
    currency:
        Currency type

    """

    def __init__(self, *args: str) -> None:
        self.version: str = args[0]
        self.date: datetime = datetime.strptime(args[1], "%Y-%m-%d")
        self.user: str = args[4]
        self.currency: str = args[7]

    def __eq__(self, __o: "ERMHDR") -> bool:
        return all(
            (
                self.version == __o.version,
                self.date == __o.date,
                self.user == __o.user,
                self.currency == __o.currency,
            )
        )

    def __hash__(self) -> int:
        return hash((self.version, self.date, self.user, self.currency))
