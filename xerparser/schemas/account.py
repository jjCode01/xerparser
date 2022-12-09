from pydantic import BaseModel


class ACCOUNT(BaseModel):
    """
    A class to represent a cost account assigned to a Task Resource.
    """

    acct_id: str
    acct_name: str
    acct_short_name: str

    def __eq__(self, __o: "ACCOUNT") -> bool:
        return (
            self.acct_name == __o.acct_name
            and self.acct_short_name == __o.acct_short_name
        )

    def __hash__(self) -> int:
        return hash((self.acct_name, self.acct_short_name))
