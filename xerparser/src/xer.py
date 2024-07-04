# xerparser
# xer.py

from itertools import groupby
from pathlib import Path
from typing import Any, BinaryIO

from xerparser.schemas import TABLE_UID_MAP
from xerparser.schemas._node import build_tree
from xerparser.schemas.account import ACCOUNT
from xerparser.schemas.actvcode import ACTVCODE
from xerparser.schemas.actvtype import ACTVTYPE
from xerparser.schemas.calendars import CALENDAR
from xerparser.schemas.ermhdr import ERMHDR
from xerparser.schemas.findates import FINDATES
from xerparser.schemas.memotype import MEMOTYPE
from xerparser.schemas.pcattype import PCATTYPE
from xerparser.schemas.pcatval import PCATVAL
from xerparser.schemas.project import PROJECT
from xerparser.schemas.projwbs import PROJWBS
from xerparser.schemas.rsrc import RSRC
from xerparser.schemas.rsrcrate import RSRCRATE
from xerparser.schemas.schedoptions import SCHEDOPTIONS
from xerparser.schemas.task import TASK, LinkToTask
from xerparser.schemas.taskfin import TASKFIN
from xerparser.schemas.taskmemo import TASKMEMO
from xerparser.schemas.taskpred import TASKPRED
from xerparser.schemas.taskrsrc import TASKRSRC
from xerparser.schemas.trsrcfin import TRSRCFIN
from xerparser.schemas.udftype import UDFTYPE
from xerparser.src.errors import CorruptXerFile, find_xer_errors
from xerparser.src.parser import CODEC, file_reader, parser


class Xer:
    """
    A class to represent the schedule data included in a .xer file.
    """

    # class variables
    CODEC = CODEC

    def __init__(self, xer_file_contents: str) -> None:
        self.tables: dict[str, list] = parser(xer_file_contents)
        if errors := find_xer_errors(self.tables):
            raise CorruptXerFile(errors)
        self.export_info = ERMHDR(*self.tables["ERMHDR"])
        self.accounts: dict[str, ACCOUNT] = build_tree(self._get_attr("ACCOUNT"))
        self.activity_code_types: dict[str, ACTVTYPE] = self._get_attr("ACTVTYPE")
        self.activity_code_values: dict[str, ACTVCODE] = build_tree(
            self._get_activity_codes()
        )
        self.calendars: dict[str, CALENDAR] = self._get_attr("CALENDAR")

        for cal in self.calendars.values():
            if cal.base_clndr_id:
                cal.base_calendar = self.calendars.get(cal.base_clndr_id)

        self.financial_periods: dict[str, FINDATES] = self._get_attr("FINDATES")
        self.notebook_topics: dict[str, MEMOTYPE] = self._get_attr("MEMOTYPE")
        self.project_code_types: dict[str, PCATTYPE] = self._get_attr("PCATTYPE")
        self.project_code_values: dict[str, PCATVAL] = build_tree(
            self._get_proj_codes()
        )
        self.resources: dict[str, RSRC] = build_tree(self._get_attr("RSRC"))
        self.resource_rates: dict[str, RSRCRATE] = self._get_rsrc_rates()
        self.sched_options: dict[str, SCHEDOPTIONS] = self._get_attr("SCHEDOPTIONS")
        self.udf_types: dict[str, UDFTYPE] = self._get_attr("UDFTYPE")
        self.projects = self._get_projects()
        self.wbs_nodes: dict[str, PROJWBS] = self._get_wbs_nodes()
        self.tasks: dict[str, TASK] = self._get_tasks()
        self.relationships: dict[str, TASKPRED] = self._get_relationships()

        self._set_proj_activity_codes()
        self._set_proj_codes()
        self._set_proj_calendars()
        self._set_task_actv_codes()
        self._set_task_memos()
        self._set_task_resources()
        self._set_financial_periods()
        self._set_udf_values()

    @classmethod
    def reader(cls, file: Path | str | BinaryIO) -> "Xer":
        """
        Create an Xer object directly from a .XER file.

        Files can be passed as a:
            * Path directory (str or pathlib.Path)
            * Binary file (from requests, Flask, FastAPI, etc...)

        """
        file_contents = file_reader(file)
        return cls(file_contents)

    def _get_activity_codes(self) -> dict[str, ACTVCODE]:
        activity_code_values = {
            code_val["actv_code_id"]: ACTVCODE(
                code_type=self.activity_code_types[code_val["actv_code_type_id"]],
                **code_val,
            )
            for code_val in self.tables.get("ACTVCODE", [])
        }
        return activity_code_values

    def _get_attr(self, table_name: str) -> dict:
        if table := self.tables.get(table_name):
            row_id = TABLE_UID_MAP[table_name]
            return {row[row_id]: eval(table_name)(**row) for row in table}
        return {}

    def _get_projects(self) -> dict[str, PROJECT]:
        projects = {
            proj["proj_id"]: PROJECT(
                self.sched_options[proj["proj_id"]],
                self.calendars.get(proj["clndr_id"]),
                **proj,
            )
            for proj in self.tables.get("PROJECT", [])
            if proj["export_flag"] == "Y"
        }
        return projects

    def _get_proj_codes(self) -> dict[str, PCATVAL]:
        project_code_values = {
            code_val["proj_catg_id"]: PCATVAL(
                code_type=self.project_code_types[code_val["proj_catg_type_id"]],
                **code_val,
            )
            for code_val in self.tables.get("PCATVAL", [])
        }

        return project_code_values

    def _get_relationships(self) -> dict[str, TASKPRED]:
        return {
            rel["task_pred_id"]: self._set_taskpred(**rel)
            for rel in self.tables.get("TASKPRED", [])
        }

    def _get_rsrc_rates(self) -> dict[str, RSRCRATE]:
        return {
            rr["rsrc_rate_id"]: self._set_rsrc_rates(**rr)
            for rr in self.tables.get("RSRCRATE", [])
        }

    def _get_tasks(self) -> dict[str, TASK]:
        return {
            task["task_id"]: self._set_task(**task)
            for task in self.tables.get("TASK", [])
        }

    def _get_wbs_nodes(self) -> dict[str, PROJWBS]:
        nodes: dict[str, PROJWBS] = self._get_attr("PROJWBS")
        for node in nodes.values():
            node.parent = nodes.get(node.parent_id)
            if node.parent:
                node.parent.addChild(node)
            if proj := self.projects.get(node.proj_id):
                proj.wbs_nodes.append(node)
                if node.is_proj_node:
                    proj.wbs_root = node
        return nodes

    def _set_proj_activity_codes(self) -> None:
        code_group = groupby(
            sorted(self.activity_code_types.values(), key=proj_key), proj_key
        )
        for proj_id, codes in code_group:
            if proj := self.projects.get(proj_id):
                proj.activity_codes = list(codes)

    def _set_proj_calendars(self) -> None:
        for project in self.projects.values():
            cal_list = []
            for cal in self.calendars.values():
                if not cal.proj_id or cal.proj_id == project.uid:
                    cal_list.append(cal)
            project.calendars = cal_list

    def _set_proj_codes(self) -> None:
        for proj_code in self.tables.get("PROJPCAT", []):
            proj = self.projects.get(proj_code["proj_id"])
            code = self.project_code_values.get(proj_code["proj_catg_id"])
            if proj and code:
                proj.project_codes.update({code.code_type: code})

    def _set_task_actv_codes(self) -> None:
        for act_code in self.tables.get("TASKACTV", []):
            task = self.tasks.get(act_code["task_id"])
            code_value = self.activity_code_values.get(act_code["actv_code_id"])
            if task and code_value:
                task.activity_codes.update({code_value.code_type: code_value})

    def _set_task_memos(self) -> None:
        for memo in self.tables.get("TASKMEMO", []):
            self._set_memo(**memo)

    def _set_task_resources(self) -> None:
        for res in self.tables.get("TASKRSRC", []):
            self._set_taskrsrc(**res)

    def _set_udf_values(self) -> None:
        for udf in self.tables.get("UDFVALUE", []):
            udf_type = self.udf_types[udf["udf_type_id"]]
            udf_value = UDFTYPE.get_udf_value(udf_type, **udf)
            if udf_type.table == "TASK":
                self.tasks[udf["fk_id"]].user_defined_fields[udf_type] = udf_value
            elif udf_type.table == "PROJECT":
                self.projects[udf["fk_id"]].user_defined_fields[udf_type] = udf_value
            elif udf_type.table == "PROJWBS":
                self.wbs_nodes[udf["fk_id"]].user_defined_fields[udf_type] = udf_value
            elif udf_type.table == "RSRC":
                self.resources[udf["fk_id"]].user_defined_fields[udf_type] = udf_value

    def _set_financial_periods(self) -> None:
        for task_fin in self.tables.get("TASKFIN", []):
            self._set_taskfin(**task_fin)

        for rsrc_fin in self.tables.get("TRSRCFIN", []):
            self._set_taskrsrc_fin(**rsrc_fin)

    def _set_memo(self, **kwargs) -> None:
        topic = self.notebook_topics[kwargs["memo_type_id"]].topic
        task = self.tasks[kwargs["task_id"]]
        task.memos.append(TASKMEMO(topic=topic, **kwargs))

    def _set_rsrc_rates(self, **kwargs) -> RSRCRATE:
        rsrc = self.resources[kwargs["rsrc_id"]]
        rsrc_rate = RSRCRATE(rsrc, **kwargs)
        return rsrc_rate

    def _set_task(self, **kwargs) -> TASK:
        calendar = self.calendars[kwargs["clndr_id"]]
        wbs = self.wbs_nodes[kwargs["wbs_id"]]
        task = TASK(calendar=calendar, wbs=wbs, **kwargs)
        wbs.tasks.append(task)
        self.projects[task.proj_id].tasks.append(task)
        return task

    def _set_taskpred(self, **kwargs) -> TASKPRED:
        pred = self.tasks[kwargs["pred_task_id"]]
        succ = self.tasks[kwargs["task_id"]]
        task_pred = TASKPRED(predecessor=pred, successor=succ, **kwargs)
        pred.successors.append(LinkToTask(succ, task_pred.link, task_pred.lag))
        succ.predecessors.append(LinkToTask(pred, task_pred.link, task_pred.lag))
        self.projects[task_pred.proj_id].relationships.append(task_pred)
        return task_pred

    def _set_taskrsrc(self, **kwargs) -> None:
        rsrc = self.resources[kwargs["rsrc_id"]]
        account = self.accounts.get(kwargs["acct_id"])
        task = self.tasks[kwargs["task_id"]]
        proj = self.projects[kwargs["proj_id"]]
        taskrsrc = TASKRSRC(resource=rsrc, account=account, **kwargs)
        rsrc.task_rsrcs.append(taskrsrc)
        task.resources.update({taskrsrc.uid: taskrsrc})
        proj.resources.append(taskrsrc)

    def _set_taskfin(self, **kwargs) -> None:
        period = self.financial_periods[kwargs["fin_dates_id"]]
        task_fin = TASKFIN(period=period, **kwargs)
        self.tasks[task_fin.task_id].periods.append(task_fin)

    def _set_taskrsrc_fin(self, **kwargs) -> None:
        period = self.financial_periods[kwargs["fin_dates_id"]]
        rsrc_fin = TRSRCFIN(period=period, **kwargs)
        self.tasks[rsrc_fin.task_id].resources[rsrc_fin.taskrsrc_id].periods.append(
            rsrc_fin
        )


def proj_key(obj: Any) -> str:
    return (obj.proj_id, "")[obj.proj_id is None]
