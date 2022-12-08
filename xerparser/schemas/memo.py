from pydantic import BaseModel
import re
from html_sanitizer import Sanitizer
from xerparser.schemas.task import TASK


class MEMOTYPE(BaseModel):
    memo_type_id: str
    memo_type: str


class TASKMEMO(BaseModel):
    memo_id: str
    memo_type_id: str
    proj_id: str
    task_id: str
    task_memo: str


class Memo:
    def __init__(self, task: TASK, type: str, memo: str) -> None:
        self.task = task
        self.type = type
        self.memo = sanitize_memo(memo)

    def __eq__(self, __o: "Memo") -> bool:
        return self.task == __o.task and self.type == __o.type

    def __hash__(self) -> int:
        return hash((self.task, self.type))


def sanitize_memo(memo: str) -> str:
    sanitzer = Sanitizer()
    memo = re.sub(r"(\u007F+)|(ï»¿)", "", memo)
    return sanitzer.sanitize(memo)
