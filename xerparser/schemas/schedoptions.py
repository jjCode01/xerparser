# xerparser
# schedoptions.py


class SCHEDOPTIONS:
    def __init__(self, **data) -> None:
        """
        A class to represent the Schedule Options.
        """
        self.max_multiple_longest_path: int = int(data["max_multiple_longest_path"])
        self.proj_id: str = data["proj_id"]
        self.calendar_on_relationship_lag: str = data[
            "sched_calendar_on_relationship_lag"
        ]
        self.float_type: str = data["sched_float_type"]
        self.lag_early_start_flag: bool = data["sched_lag_early_start_flag"] == "Y"
        self.open_critical_flag: bool = data["sched_open_critical_flag"] == "Y"
        self.outer_depend_type: str = data["sched_outer_depend_type"]
        self.progress_override: bool = data["sched_progress_override"] == "Y"
        self.retained_logic: bool = data["sched_retained_logic"] == "Y"
        self.setplantoforecast: bool = data["sched_setplantoforecast"] == "Y"
        self.use_expect_end_flag: bool = data["sched_use_expect_end_flag"] == "Y"
        self.use_project_end_date_for_float = (
            data["sched_use_project_end_date_for_float"] == "Y"
        )
        self.schedoptions_id: str = data["schedoptions_id"]
        self.use_total_float_multiple_longest_paths: bool = (
            data["use_total_float_multiple_longest_paths"] == "Y"
        )
