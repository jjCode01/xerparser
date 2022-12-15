# xerparser
# rsrc.py

from pydantic import BaseModel, Field


class RSRC(BaseModel):
    """
    A class to represent a Resource.

    ...

    Attributes
    ----------
    uid: str
        Unique ID [rsrc_id]
    clndr_id:
        Unique ID of Calendar assigned to the resource
    name:
        Resource Name [rsrc_name]
    short_name:
        Resource ID [rsrc_short_name]
    type: str
        Resource Type [rsrc_type]
    """

    uid: str = Field(alias="rsrc_id")
    clndr_id: str
    name: str = Field(alias="rsrc_name")
    short_name: str = Field(alias="rsrc_short_name")
    type: str = Field(alias="rsrc_type")

    def __eq__(self, __o: "RSRC") -> bool:
        return all(
            (
                self.name == __o.name,
                self.short_name == __o.short_name,
                self.type == __o.type,
            )
        )

    def __hash__(self) -> int:
        return hash((self.name, self.short_name, self.type))
