# xerparser
# taskmemo.py

from pydantic import BaseModel
import re
from html_sanitizer import Sanitizer


class TASKMEMO(BaseModel):
    """A class to represent a note assigned to an activity"""

    memo_id: str
    memo_type_id: str
    proj_id: str
    task_id: str
    task_memo: str
    topic: str = None

    class config:
        arbitrary_types_allowed = True

    @property
    def memo(self):
        return sanitize_memo(self.task_memo)


def sanitize_memo(memo: str) -> str:
    sanitzer = Sanitizer()
    memo = re.sub(r"(\u007F+)|(ï»¿)", "", memo)
    return sanitzer.sanitize(memo)
