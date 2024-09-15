# xerparser
# schedoptions.py

from xerparser.src.validators import optional_int


class SCHEDOPTIONS:
    def __init__(self, **data: str) -> None:
        """
        A class to represent the Schedule Options.
        """
        self.max_multiple_longest_path: int | None = optional_int(
            data.get("max_multiple_longest_path")
        )
        self.proj_id: str = data["proj_id"]
        self.calendar_on_relationship_lag: str = data.get(
            "sched_calendar_on_relationship_lag", ""
        )
        self.float_type: str = data["sched_float_type"]
        self.lag_early_start_flag: bool = data["sched_lag_early_start_flag"] == "Y"
        self.open_critical_flag: bool = data["sched_open_critical_flag"] == "Y"
        self.outer_depend_type: str = data["sched_outer_depend_type"]
        self.progress_override: bool = data["sched_progress_override"] == "Y"
        self.retained_logic: bool = data["sched_retained_logic"] == "Y"
        self.setplantoforecast: bool = data["sched_setplantoforecast"] == "Y"
        self.use_expect_end_flag: bool = data["sched_use_expect_end_flag"] == "Y"
        self.use_project_end_date_for_float = (
            data.get("sched_use_project_end_date_for_float", "N") == "Y"
        )
        self.schedoptions_id: str = data["schedoptions_id"]
        self.use_total_float_multiple_longest_paths: bool = (
            data.get("use_total_float_multiple_longest_paths", "N") == "Y"
        )

    def __eq__(self, __o: "SCHEDOPTIONS") -> bool:
        return all(
            (
                self.max_multiple_longest_path == __o.max_multiple_longest_path,
                self.calendar_on_relationship_lag == __o.calendar_on_relationship_lag,
                self.float_type == __o.float_type,
                self.lag_early_start_flag == __o.lag_early_start_flag,
                self.open_critical_flag == __o.open_critical_flag,
                self.outer_depend_type == __o.outer_depend_type,
                self.progress_override == __o.progress_override,
                self.retained_logic == __o.retained_logic,
                self.setplantoforecast == __o.setplantoforecast,
                self.use_expect_end_flag == __o.use_expect_end_flag,
                self.use_project_end_date_for_float
                == __o.use_project_end_date_for_float,
                self.use_total_float_multiple_longest_paths
                == __o.use_total_float_multiple_longest_paths,
            )
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.max_multiple_longest_path,
                self.calendar_on_relationship_lag,
                self.float_type,
                self.lag_early_start_flag,
                self.open_critical_flag,
                self.outer_depend_type,
                self.progress_override,
                self.retained_logic,
                self.setplantoforecast,
                self.use_expect_end_flag,
                self.use_project_end_date_for_float,
                self.use_total_float_multiple_longest_paths,
            )
        )
