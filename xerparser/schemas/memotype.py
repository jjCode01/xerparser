# xerparser
# memotype.py

from pydantic import BaseModel, Field


class MEMOTYPE(BaseModel):
    """
    A class to represent a notebook topic.

    ...

    Attributes
    ----------
    uid: str
        Unique ID [memo_type_id]
    topic: str
        Notebook Topic [memo_type]
    """

    uid: str = Field(alias="memo_type_id")
    topic: str = Field(alias="memo_type")
