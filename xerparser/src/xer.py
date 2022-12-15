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


__all__ = ("Xer",)


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

        self.wbs: dict[str, PROJWBS] = {
            wbs["wbs_id"]: self._set_wbs(**wbs)
            for wbs in _tables.get("PROJWBS", [])
            if wbs["proj_id"] in self.projects
        }

        self.tasks: dict[str, TASK] = {
            task["task_id"]: self._set_task(**task)
            for task in _tables.get("TASK", [])
            if task["proj_id"] in self.projects
        }

        self.task_resources: dict[str, TASKRSRC] = {
            res["taskrsrc_id"]: self._set_taskrsrc(**res)
            for res in _tables.get("TASKRSRC", [])
            if res["proj_id"] in self.projects
        }

        self.task_notes: list[TASKMEMO] = sorted(
            [self._set_memo(**note) for note in _tables.get("TASKMEMO", [])],
            key=lambda n: n.task_id,
        )

        self.relationships: dict[tuple, TASKPRED] = {
            rel["task_pred_id"]: self._set_taskpred(**rel)
            for rel in _tables.get("TASKPRED", [])
            if rel["proj_id"] in self.projects and rel["pred_proj_id"] in self.projects
        }

        self._link_table_data()

    def _link_table_data(self) -> None:
        for wbs in self.wbs.values():
            if not wbs.is_proj_node:
                wbs.parent = self.wbs[wbs.parent_wbs_id]

        def sort_proj(obj):
            return obj.proj_id

        for proj_id, wbs in groupby(
            sorted(self.wbs.values(), key=sort_proj), sort_proj
        ):
            self.projects[proj_id].wbs = tuple(wbs)

        for proj_id, tasks in groupby(
            sorted(self.tasks.values(), key=sort_proj), sort_proj
        ):
            self.projects[proj_id].tasks = tuple(tasks)

        for proj_id, relationships in groupby(
            sorted(self.relationships.values(), key=sort_proj), sort_proj
        ):
            self.projects[proj_id].relationships = tuple(relationships)

        for proj_id, task_rsrcs in groupby(
            sorted(self.task_resources.values(), key=sort_proj), sort_proj
        ):
            self.projects[proj_id].resources = tuple(task_rsrcs)

    def _set_memo(self, **kwargs) -> TASKMEMO:
        topic = self.notebooks[kwargs["memo_type_id"]].topic
        task = self.tasks[kwargs["task_id"]]
        return TASKMEMO(task=task, topic=topic, **kwargs)

    def _set_task(self, **kwargs) -> TASK:
        calendar = self.calendars[kwargs["clndr_id"]]
        calendar.assignments += 1
        wbs = self.wbs[kwargs["wbs_id"]]
        wbs.assignments += 1
        return TASK(calendar=calendar, wbs=wbs, **kwargs)

    def _set_taskpred(self, **kwargs) -> TASKPRED:
        pred = self.tasks[kwargs["pred_task_id"]]
        succ = self.tasks[kwargs["task_id"]]
        return TASKPRED(predecessor=pred, successor=succ, **kwargs)

    def _set_taskrsrc(self, **kwargs) -> TASKRSRC:
        rsrc = self.resources.get(kwargs["rsrc_id"])
        account = self.accounts.get(kwargs["acct_id"])
        task = self.tasks.get(kwargs["task_id"])
        return TASKRSRC(task=task, resource=rsrc, account=account, **kwargs)

    def _set_wbs(self, **kwargs) -> PROJWBS:
        wbs = PROJWBS(**kwargs)
        if wbs.is_proj_node and (proj := self.projects.get(wbs.proj_id)):
            proj.name = wbs.name

        return wbs


if __name__ == "__main__":
    from pathlib import Path

    directory = "/home/jesse/xer_files/"
    # xer_directory = os.path.join(directory, "xer_files")
    files = Path(directory).glob("*.xer")

    for file in files:
        print(file)
        xer = Xer(file)
        print(xer.export.version, xer.export.date)
        for proj in xer.projects.values():
            print(
                proj.short_name,
                proj.name,
                f"\n\tData Date: {proj.data_date: %d-%b-%Y}",
                f"\n\tEnd Date: {proj.finish_date: %d-%b-%Y}",
                f"\n\tTasks: {len(proj.tasks):,}",
                f"\n\tRelationships: {len(proj.relationships):,}",
                f"\n\tBudgeted Cost: {proj.budgeted_cost:,.2f}",
            )
            print("------------------------------\n")
