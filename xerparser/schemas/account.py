# xerparser
# account.py

from pydantic import BaseModel, Field, validator


class ACCOUNT(BaseModel):
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

    uid: str = Field(alias="acct_id")
    code: str = Field("acct_short_name")
    description: str = Field("acct_desc")
    name: str = Field("acct_name")

    @validator("description", pre=True)
    def _check_description(cls, value: str) -> str:
        return (value, "")[value == "" or value == "ï»¿"]

    def __eq__(self, __o: "ACCOUNT") -> bool:
        return self.name == __o.name and self.code == __o.code

    def __hash__(self) -> int:
        return hash((self.name, self.name))
