# xerparser
# taskmemo.py

from pydantic import BaseModel, Field, validator
import re
from html_sanitizer import Sanitizer
from xerparser.schemas.task import TASK


class TASKMEMO(BaseModel):
    """A class to represent a note assigned to an activity"""

    uid: str = Field(alias="memo_id")
    memo_type_id: str
    proj_id: str
    task_id: str
    task_memo: str
    topic: str = None
    task: TASK

    class config:
        arbitrary_types_allowed = True

    def __eq__(self, __o: "TASKMEMO") -> bool:
        return self.topic == __o.topic and self.task == __o.task

    def __hash__(self) -> int:
        return hash((self.topic, self.task))

    @property
    def clean_memo(self):
        return sanitize_html(self.task_memo)


def sanitize_html(memo: str) -> str:
    sanitzer = Sanitizer()
    memo = re.sub(r"(\u007F+)|(ï»¿)", "", memo)
    return sanitzer.sanitize(memo)
