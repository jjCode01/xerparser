# xerparser
# xer.py

from itertools import groupby
from collections import defaultdict
from xerparser.src.parser import xer_to_dict
from xerparser.schemas.account import ACCOUNT
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.memotype import MEMOTYPE
from xerparser.schemas.project import PROJECT
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.rsrc import RSRC
from xerparser.schemas.task import TASK
from xerparser.schemas.taskmemo import TASKMEMO
from xerparser.schemas.taskpred import TASKPRED
from xerparser.schemas.taskrsrc import TASKRSRC
from xerparser.schemas.ermhdr import ERMHDR


class Xer:
    def __init__(self, file: bytes | str) -> None:
        _xer = xer_to_dict(file)

        self.export = ERMHDR(*_xer["ERMHDR"])
        self.errors = _xer["errors"]

        _tables: dict[str, list] = _xer["tables"]
        self.accounts: dict[str, ACCOUNT] = {
            acct["acct_id"]: ACCOUNT(**acct) for acct in _tables.get("ACCOUNT", [])
        }

        self.notebooks: dict[str, MEMOTYPE] = {
            topic["memo_type_id"]: MEMOTYPE(**topic)
            for topic in _tables.get("MEMOTYPE", [])
        }

        self.resources: dict[str, RSRC] = {
            rsrc["rsrc_id"]: RSRC(**rsrc) for rsrc in _tables.get("RSRC", [])
        }

        self.calendars: dict[str, CALENDAR] = {
            cal["clndr_id"]: CALENDAR(**cal) for cal in _tables.get("CALENDAR", [])
        }

        self.projects: dict[str, PROJECT] = {
            proj["proj_id"]: PROJECT(**proj)
            for proj in _tables.get("PROJECT", [])
            if proj["export_flag"] == "Y"
        }

        for wbs in _tables.get("PROJWBS", []):
            if proj := self.projects.get(wbs["proj_id"]):
                proj.wbs[wbs["wbs_id"]] = self._set_wbs(**wbs)

        for task in _tables.get("TASK", []):
            if proj := self.projects.get(task["proj_id"]):
                proj.tasks[task["task_id"]] = self._set_task(**task)

        for res in _tables.get("TASKRSRC", []):
            if proj := self.projects.get(res["proj_id"]):
                proj.tasks[res["task_id"]].resources.append(self._set_taskrsrc(**res))

        for memo in _tables.get("TASKMEMO", []):
            if proj := self.projects.get(memo["proj_id"]):
                proj.tasks[memo["task_id"]].memos.append(self._set_memo(**memo))

        for rel in _tables.get("TASKPRED", []):
            if proj := self.projects.get(rel["proj_id"]):
                proj.relationships[rel["task_pred_id"]] = self._set_taskpred(**rel)

        for proj in self.projects.values():
            for wbs in proj.wbs.values():
                # if not wbs.is_proj_node:
                wbs.parent = proj.wbs.get(wbs.parent_wbs_id)

    def _set_memo(self, **kwargs) -> TASKMEMO:
        topic = self.notebooks[kwargs["memo_type_id"]].topic
        task = self.projects[kwargs["proj_id"]].tasks[kwargs["task_id"]]
        return TASKMEMO(task=task, topic=topic, **kwargs)

    def _set_task(self, **kwargs) -> TASK:
        calendar = self.calendars.get(kwargs["clndr_id"])
        if calendar:
            self.projects[kwargs["proj_id"]].calendars.add(calendar)
        wbs = self.projects[kwargs["proj_id"]].wbs[kwargs["wbs_id"]]
        wbs.assignments += 1
        return TASK(calendar=calendar, wbs=wbs, **kwargs)

    def _set_taskpred(self, **kwargs) -> TASKPRED:
        pred = self.projects[kwargs["pred_proj_id"]].tasks[kwargs["pred_task_id"]]
        succ = self.projects[kwargs["proj_id"]].tasks[kwargs["task_id"]]
        return TASKPRED(predecessor=pred, successor=succ, **kwargs)

    def _set_taskrsrc(self, **kwargs) -> TASKRSRC:
        rsrc = self.resources.get(kwargs["rsrc_id"])
        account = self.accounts.get(kwargs["acct_id"])
        task = self.projects[kwargs["proj_id"]].tasks[kwargs["task_id"]]
        return TASKRSRC(task=task, resource=rsrc, account=account, **kwargs)

    def _set_wbs(self, **kwargs) -> PROJWBS:
        wbs = PROJWBS(**kwargs)
        if wbs.is_proj_node and (proj := self.projects.get(wbs.proj_id)):
            proj.name = wbs.name

        return wbs
