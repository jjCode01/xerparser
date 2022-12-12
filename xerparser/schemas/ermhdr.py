# xerparser
# ermhdr.py

from datetime import datetime


class ERMHDR:
    def __init__(self, *args) -> None:
        self.version = args[0]
        self.date = datetime.strptime(args[1], "%Y-%m-%d")
        self.user = args[4]
        self.currency = args[7]
