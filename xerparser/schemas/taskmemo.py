# xerparser
# taskmemo.py

from pydantic import BaseModel, Field, validator
import re
from html_sanitizer import Sanitizer


class TASKMEMO(BaseModel):
    """A class to represent a note assigned to an activity"""

    uid: str = Field(alias="memo_id")
    memo: str = Field(alias="task_memo")
    memo_type_id: str
    proj_id: str
    task_id: str
    topic: str

    class config:
        arbitrary_types_allowed = True

    @validator("memo", pre=True)
    def sanitize_html(value) -> str:
        sanitzer = Sanitizer()
        memo = re.sub(r"(\u007F+)|(ï»¿)", "", value)
        return sanitzer.sanitize(memo)

    def __eq__(self, __o: "TASKMEMO") -> bool:
        return self.topic == __o.topic

    def __hash__(self) -> int:
        return hash(self.topic)
