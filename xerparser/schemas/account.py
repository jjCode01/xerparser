# xerparser
# account.py


class ACCOUNT:
    """
    A class to represent a cost account.

    ...

    Attributes
    ----------
    uid: str
        Unique ID [acct_id]
    code: str
        Cost Account ID or Cost Code [acct_short_name]
    description: str
        Cost Account Description [acct_desc]
    name: str
        Cost Account Name [acct_name]
    """

    def __init__(self, **data) -> None:
        self.uid: str = data["acct_id"]
        self.code: str = data["acct_short_name"]
        self.description: str = _check_description(data["acct_descr"])
        self.name: str = data["acct_name"]

    def __eq__(self, __o: "ACCOUNT") -> bool:
        return self.name == __o.name and self.code == __o.code

    def __hash__(self) -> int:
        return hash((self.name, self.code))


def _check_description(value: str) -> str:
    return (value, "")[value == "" or value == "ï»¿"]
