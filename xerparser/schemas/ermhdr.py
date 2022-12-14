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

    def __init__(self, *args) -> None:
        self.version: str = args[0]
        self.date: datetime = datetime.strptime(args[1], "%Y-%m-%d")
        self.user: str = args[4]
        self.currency: str = args[7]
