# xerparser
# xer.py

from itertools import groupby
from typing import Any

from xerparser.src.errors import find_xer_errors
from xerparser.src.parser import xer_to_dict

from xerparser.schemas.account import ACCOUNT
from xerparser.schemas.actvcode import ACTVCODE
from xerparser.schemas.actvtype import ACTVTYPE
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.findates import FINDATES
from xerparser.schemas.memotype import MEMOTYPE
from xerparser.schemas.project import PROJECT
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.rsrc import RSRC
from xerparser.schemas.task import TASK, LinkToTask
from xerparser.schemas.taskfin import TASKFIN
from xerparser.schemas.taskmemo import TASKMEMO
from xerparser.schemas.taskpred import TASKPRED
from xerparser.schemas.taskrsrc import TASKRSRC
from xerparser.schemas.trsrcfin import TRSRCFIN
from xerparser.schemas.ermhdr import ERMHDR


class Xer:
    """
    A class to represent the schedule data included in a .xer file.
    """

    # class variables
    CODEC = "cp1252"

    def __init__(self, xer_file_contents: str) -> None:
        _xer = xer_to_dict(xer_file_contents)

        self.export_info = ERMHDR(*_xer["ERMHDR"])
        self.errors = find_xer_errors(_xer)
        self.accounts = {
            acct["acct_id"]: ACCOUNT(**acct) for acct in _xer.get("ACCOUNT", [])
        }
        self.activity_code_types = {
            code_type["actv_code_type_id"]: ACTVTYPE(**code_type)
            for code_type in _xer.get("ACTVTYPE", [])
        }
        self.activity_code_values = {
            code_val["actv_code_id"]: ACTVCODE(
                code_type=self.activity_code_types[code_val["actv_code_type_id"]],
                **code_val,
            )
            for code_val in _xer.get("ACTVCODE", [])
        }
        for act_code in self.activity_code_values.values():
            act_code.parent = self.activity_code_values.get(
                act_code.parent_actv_code_id
            )

        self.calendars = {
            clndr["clndr_id"]: CALENDAR(**clndr) for clndr in _xer.get("CALENDAR", [])
        }
        self.financial_periods = {
            fin_per["fin_dates_id"]: FINDATES(**fin_per)
            for fin_per in _xer.get("FINDATES", [])
        }
        self.notebook_topics = {
            topic["memo_type_id"]: MEMOTYPE(**topic)
            for topic in _xer.get("MEMOTYPE", [])
        }
        self.projects = {
            proj["proj_id"]: PROJECT(**proj)
            for proj in _xer.get("PROJECT", [])
            if proj["export_flag"] == "Y"
        }
        self.resources = {
            rsrc["rsrc_id"]: RSRC(**rsrc) for rsrc in _xer.get("RSRC", [])
        }
        self.wbs_nodes: dict[str, PROJWBS] = {
            node["wbs_id"]: self._set_wbs(**node) for node in _xer.get("PROJWBS", [])
        }
        for node in self.wbs_nodes.values():
            node.parent = self.wbs_nodes.get(node.parent_wbs_id)

        self.tasks: dict[str, TASK] = {
            task["task_id"]: self._set_task(**task) for task in _xer.get("TASK", [])
        }
        self.relationships: dict[str, TASKPRED] = {
            rel["task_pred_id"]: self._set_taskpred(**rel)
            for rel in _xer.get("TASKPRED", [])
        }

        for act_code in _xer.get("TASKACTV", []):
            if task := self.tasks.get(act_code["task_id"]):
                if code_value := self.activity_code_values.get(
                    act_code["actv_code_id"]
                ):
                    task.activity_codes.update({code_value.code_type: code_value})

        self._set_project_attrs(_xer)
        self._set_task_attrs(_xer)

    def _set_project_attrs(self, xer: dict) -> None:
        def proj_key(obj: Any) -> str:
            return (obj.proj_id, "")[obj.proj_id is None]

        clndr_group = groupby(sorted(self.calendars.values(), key=proj_key), proj_key)
        for proj_id, clndrs in clndr_group:
            if proj := self.projects.get(proj_id):
                proj.calendars = list(clndrs)

        wbs_group = groupby(sorted(self.wbs_nodes.values(), key=proj_key), proj_key)
        for proj_id, wbs_nodes in wbs_group:
            if proj := self.projects.get(proj_id):
                proj.wbs_nodes = list(wbs_nodes)

        task_group = groupby(sorted(self.tasks.values(), key=proj_key), proj_key)
        for proj_id, tasks in task_group:
            if proj := self.projects.get(proj_id):
                proj.tasks = list(tasks)

        act_code_group = groupby(
            sorted(self.activity_code_types.values(), key=proj_key), proj_key
        )
        for proj_id, codes in act_code_group:
            if proj := self.projects.get(proj_id):
                proj.activity_codes = list(codes)

        rel_group = groupby(sorted(self.relationships.values(), key=proj_key), proj_key)
        for proj_id, rels in rel_group:
            if proj := self.projects.get(proj_id):
                proj.relationships = [
                    rel for rel in list(rels) if rel.pred_proj_id == proj.uid
                ]

    def _set_task_attrs(self, xer: dict) -> None:
        for res in xer.get("TASKRSRC", []):
            self.tasks[res["task_id"]].resources.update(**self._set_taskrsrc(**res))

        for memo in xer.get("TASKMEMO", []):
            self.tasks[memo["task_id"]].memos.append(self._set_memo(**memo))

        for task_fin in xer.get("TASKFIN", []):
            self.tasks[task_fin["task_id"]].periods.append(
                self._set_taskfin(**task_fin)
            )

        for rsrc_fin in xer.get("TRSRCFIN", []):
            self.tasks[rsrc_fin["task_id"]].resources[
                rsrc_fin["taskrsrc_id"]
            ].periods.append(self._set_taskrsrc_fin(**rsrc_fin))

    def _set_act_code_type(self, **kwargs) -> dict[str, ACTVTYPE]:
        return {kwargs["actv_code_type_id"]: ACTVTYPE(**kwargs)}

    def _set_memo(self, **kwargs) -> TASKMEMO:
        topic = self.notebook_topics[kwargs["memo_type_id"]].topic
        task = self.tasks[kwargs["task_id"]]
        return TASKMEMO(task=task, topic=topic, **kwargs)

    def _set_task(self, **kwargs) -> TASK:
        calendar = self.calendars.get(kwargs["clndr_id"])
        wbs = self.wbs_nodes[kwargs["wbs_id"]]
        wbs.assignments += 1
        task = TASK(calendar=calendar, wbs=wbs, **kwargs)
        return task

    def _set_taskpred(self, **kwargs) -> TASKPRED:
        pred = self.tasks[kwargs["pred_task_id"]]
        succ = self.tasks[kwargs["task_id"]]
        task_pred = TASKPRED(predecessor=pred, successor=succ, **kwargs)
        pred.successors.append(LinkToTask(succ, task_pred.link, task_pred.lag))
        succ.predecessors.append(LinkToTask(pred, task_pred.link, task_pred.lag))
        return task_pred

    def _set_taskrsrc(self, **kwargs) -> dict[str, TASKRSRC]:
        rsrc = self.resources.get(kwargs["rsrc_id"])
        account = self.accounts.get(kwargs["acct_id"])
        task = self.tasks[kwargs["task_id"]]
        taskrsrc = TASKRSRC(resource=rsrc, account=account, **kwargs)
        return {taskrsrc.uid: taskrsrc}

    def _set_taskfin(self, **kwargs) -> TASKFIN:
        period = self.financial_periods[kwargs["fin_dates_id"]]
        return TASKFIN(period=period, **kwargs)

    def _set_taskrsrc_fin(self, **kwargs) -> TRSRCFIN:
        period = self.financial_periods[kwargs["fin_dates_id"]]
        return TRSRCFIN(period=period, **kwargs)

    def _set_wbs(self, **kwargs) -> PROJWBS:
        wbs = PROJWBS(**kwargs)
        if wbs.is_proj_node and (proj := self.projects.get(wbs.proj_id)):
            proj.name = wbs.name
        return wbs
