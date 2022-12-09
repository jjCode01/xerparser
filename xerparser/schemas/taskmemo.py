from pydantic import BaseModel
import re
from html_sanitizer import Sanitizer
from xerparser.schemas.task import TASK
from xerparser.schemas.memotype import MEMOTYPE


class TASKMEMO(BaseModel):
    memo_id: str
    memo_type_id: str
    proj_id: str
    task_id: str
    task_memo: str
    task: TASK = None
    type: MEMOTYPE = None

    class config:
        arbitrary_types_allowed = True

    @property
    def memo(self):
        return sanitize_memo(self.task_memo)


def sanitize_memo(memo: str) -> str:
    sanitzer = Sanitizer()
    memo = re.sub(r"(\u007F+)|(ï»¿)", "", memo)
    return sanitzer.sanitize(memo)
