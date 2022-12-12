# xerparser
# account.py

from pydantic import BaseModel, Field


class ACCOUNT(BaseModel):
    """
    A class to represent a cost account.

    ...

    Attributes
    ----------
    uid: str
        Unique ID [acct_id]
    description: str
        Cost Account Description [acct_desc]
    name: str
        Cost Account Name [acct_name]
    cost_code: str
        Cost Account ID or Cost Code [acct_short_name]

    """

    uid: str = Field(alias="acct_id")
    description: str | None
    name: str = Field(alias="acct_name")
    cost_code: str = Field(alias="acct_short_name")

    def __eq__(self, __o: "ACCOUNT") -> bool:
        return self.name == __o.name and self.cost_code == __o.cost_code

    def __hash__(self) -> int:
        return hash((self.name, self.short_name))
