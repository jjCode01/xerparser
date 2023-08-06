# xerparser
# taskmemo.py

import re
from html_sanitizer import Sanitizer
from typing import Any


class TASKMEMO:
    """A class to represent a note assigned to an activity"""

    def __init__(self, **data: Any) -> None:
        self.uid: str = data["memo_id"]
        self.memo: str = _sanitize_html(data["task_memo"])
        self.memo_type_id: str = data["memo_type_id"]
        self.proj_id: str = data["proj_id"]
        self.task_id: str = data["task_id"]
        self.topic: str = data["topic"]

    def __eq__(self, __o: "TASKMEMO") -> bool:
        return self.topic == __o.topic

    def __hash__(self) -> int:
        return hash(self.topic)


def _sanitize_html(value) -> str:
    re_remove = re.compile(r"(\u007F+)|(ï»¿)")
    sanitzer = Sanitizer()
    memo = re.sub(re_remove, "", value)
    return sanitzer.sanitize(memo)
