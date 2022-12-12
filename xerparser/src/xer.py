# xerparser
# xer.py

from itertools import groupby
from typing import Iterator
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
            wbs["wbs_id"]: PROJWBS(**wbs)
            for wbs in _tables.get("PROJWBS", [])
            if wbs["proj_id"] in self.projects
        }

        self.tasks: dict[str, TASK] = {
            task.task_id: task for task in self._iter_tasks(_tables.get("TASK", []))
        }

        self.task_notes: dict[tuple, TASKMEMO] = {
            note.memo_id: note for note in self._iter_memos(_tables.get("TASKMEMO", []))
        }

        self.relationships: dict[tuple, TASKPRED] = {
            (rel.predecessor.task_code, rel.successor.task_code, rel.link): rel
            for rel in self._iter_relationships(_tables.get("TASKPRED", []))
        }

        self.task_resources: dict[tuple, TASKRSRC] = {
            res.taskrsrc_id: res
            for res in self._iter_resources(_tables.get("TASKRSRC", []))
        }

        self._link_table_data()

    def _link_table_data(self) -> None:
        for wbs in self.wbs.values():
            if not wbs.is_project_node:
                wbs.parent = self.wbs[wbs.parent_wbs_id]
            else:
                self.projects[wbs.proj_id].name = wbs.wbs_name

        for task, succ_logic in groupby(
            self.relationships.values(), lambda r: r.predecessor
        ):
            task.successors = tuple(succ_logic)

        for task, pred_logic in groupby(
            self.relationships.values(), lambda r: r.successor
        ):
            task.predecessors = tuple(pred_logic)

        for task_id, resources in groupby(
            self.task_resources.values(), lambda r: r.task_id
        ):
            self.tasks[task_id].resources = tuple(resources)

        for proj_id, wbs in groupby(self.wbs.values(), lambda r: r.proj_id):
            self.projects[proj_id].wbs = tuple(wbs)

        for proj_id, tasks in groupby(self.tasks.values(), lambda t: t.proj_id):
            self.projects[proj_id].tasks = tuple(tasks)

        for proj_id, relationships in groupby(
            self.relationships.values(), lambda r: r.proj_id
        ):
            self.projects[proj_id].relationships = tuple(relationships)

    def _iter_tasks(self, table: list) -> Iterator[TASK]:
        for task in table:
            if task["proj_id"] in self.projects:
                calendar = self.calendars[task["clndr_id"]]
                calendar.assignments += 1
                wbs = self.wbs[task["wbs_id"]]
                wbs.assignments += 1
                yield TASK(calendar=calendar, wbs=wbs, **task)

    def _iter_memos(self, table: list) -> Iterator[TASKMEMO]:
        for memo in table:
            if memo["proj_id"] in self.projects:
                # task = self.tasks[memo["task_id"]]
                topic = self.notebooks[memo["memo_type_id"]].memo_type
                yield TASKMEMO(topic=topic, **memo)

    def _iter_relationships(self, table: list) -> Iterator[TASKPRED]:
        for rel in table:
            if rel["proj_id"] in self.projects and rel["pred_proj_id"] in self.projects:
                pred = self.tasks[rel["pred_task_id"]]
                succ = self.tasks[rel["task_id"]]
                yield TASKPRED(predecessor=pred, successor=succ, **rel)

    def _iter_resources(self, table: list) -> Iterator[TASKRSRC]:
        for res in table:
            if res["proj_id"] in self.projects:
                task = self.tasks[res["task_id"]]
                rsrc = self.resources.get(res["rsrc_id"])
                account = self.accounts.get(res["acct_id"])
                yield TASKRSRC(task=task, resource=rsrc, account=account, **res)


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
                proj.proj_short_name,
                proj.name,
                f"\n\tData Date: {proj.data_date: %d-%b-%Y}",
                f"\n\tEnd Date: {proj.finish_date: %d-%b-%Y}",
                f"\n\tTasks: {len(proj.tasks):,}",
                f"\n\tRelationships: {len(proj.relationships):,}",
            )
            print("------------------------------\n")
