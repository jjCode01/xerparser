# xerparser
# calendars.py


import re
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from functools import cached_property
from typing import Iterator, Optional

from xerparser.scripts.dates import (
    calc_time_var_hrs,
    clean_date,
    clean_dates,
    conv_time,
)
from xerparser.src.validators import optional_date, optional_str

WEEKDAYS = (
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
)


class ClndrRegEx(Enum):
    """Regular Expressions used to parse the Calendar Data"""

    weekdays = re.compile(
        r"(?<=0\|\|)[1-7]\(\).+?(?=\(0\|\|[1-7]\(\)|\(0\|\|VIEW|\(0\|\|Exceptions|\)$)"
    )
    shifts = re.compile(r"[sf]\|[0-2]?\d:[0-5]\d\|[sf]\|[0-2]?\d:[0-5]\d")
    shift_hours = re.compile(r"[0-2]?\d:[0-5]\d")
    holidays = re.compile(r"(?<=d\|)\d{5}(?=\)\(\))")
    exceptions = re.compile(r"(?<=d\|)\d{5}\)\([^\)]{1}.+?\(\)\)\)")


@dataclass(frozen=True)
class WeekDay:
    """
    A class to represent a weekday.

    ...

    Attributes
    ----------
    week_day: str
        Day of week (Monday, Tuesday, Wednesday, etc...)
    shifts: list
        List of start and stop work times
    hours: int
        Total work hours for the day
    start: time
        Start work time
    finish: time
        Finish work time
    """

    week_day: str
    shifts: list[tuple[time, time]] = field(default_factory=list)
    hours: float = field(init=False, default=0)
    start: time = field(init=False, default=time(0, 0, 0, 0))
    finish: time = field(init=False, default=time(0, 0, 0, 0))

    def __post_init__(self):
        """
        Calculate properties after the object has been initialized
        """
        if self.shifts:
            shift_times = [hr for shift in self.shifts for hr in shift]
            object.__setattr__(
                self,
                "hours",
                sum(calc_time_var_hrs(shift[0], shift[1]) for shift in self.shifts),
            )

            object.__setattr__(self, "start", min(shift_times))
            object.__setattr__(self, "finish", max(shift_times))

    def __len__(self) -> int:
        return len(self.shifts)

    def __bool__(self) -> bool:
        """[False] if hours == 0; [True] is hours > 0."""
        return self.hours != 0


class CALENDAR:
    """
    A class to represent a schedule Calendar.
    """

    class CalendarType(Enum):
        CA_Base = "Global"
        CA_Rsrc = "Resource"
        CA_Project = "Project"

    def __init__(self, **data: str) -> None:
        self.uid: str = data["clndr_id"]
        self.base_clndr_id: str | None = optional_str(data["base_clndr_id"])
        self.data: str = data["clndr_data"]
        self.is_default: bool = data["default_flag"] == "Y"
        self.last_chng_date: datetime | None = optional_date(data["last_chng_date"])
        self.name: str = data["clndr_name"]
        self.proj_id: str | None = optional_str(data["proj_id"])
        self.type: CALENDAR.CalendarType = CALENDAR.CalendarType[data["clndr_type"]]
        self.base_calendar: Optional["CALENDAR"] = None

    def __eq__(self, __o: "CALENDAR") -> bool:
        return self.name == __o.name and self.type == __o.type

    def __gt__(self, __o: "CALENDAR") -> bool:
        if self.name == __o.name:
            return self.type.value > __o.type.value
        return self.name > __o.name

    def __lt__(self, __o: "CALENDAR") -> bool:
        if self.name == __o.name:
            return self.type.value < __o.type.value
        return self.name < __o.name

    def __len__(self) -> int:
        return sum(day.hours > 0 for day in self.work_week.values())

    def __hash__(self) -> int:
        return hash((self.name, self.type))

    def __str__(self) -> str:
        return f"{self.name} [{self.type}]"

    @staticmethod
    def conv_excel_date(ordinal: int, _epoch0=datetime(1899, 12, 31)) -> datetime:
        """Convert Excel date format to datetime object"""
        if ordinal < 0 or not isinstance(ordinal, int):
            raise ValueError("Innappropiate value passed, should be positive integer.")

        # Excel leap year bug, 1900 is not a leap year
        if ordinal >= 60:
            ordinal -= 1

        return (_epoch0 + timedelta(days=ordinal)).replace(
            microsecond=0, second=0, minute=0, hour=0
        )

    @cached_property
    def holidays(self) -> list[datetime]:
        """Parse non-workday exceptions from Calendar data field."""
        nonwork_days = []
        for e in _parse_clndr_data(self.data, ClndrRegEx.holidays.value):
            _date = self.conv_excel_date(int(e))

            # Verify exception is not already a non-work day on the standard calendar
            if self.work_week.get(f"{_date:%A}"):
                nonwork_days.append(_date)

        return nonwork_days

    def is_workday(self, date_to_check: datetime) -> bool:
        """Checks if a date is a workday in a Calendar object"""

        if not isinstance(date_to_check, datetime):
            raise ValueError("Argument date_to_check must be a datetime object")

        # _date = date_to_check.date
        _date = clean_date(date_to_check)
        if _date in self.holidays:
            return False
        if (
            not self.holidays
            and self.base_calendar
            and _date in self.base_calendar.holidays
        ):
            return False
        if _date in self.work_exceptions.keys():
            return True
        return bool(self.work_week[f"{date_to_check:%A}"])

    def iter_holidays(self, start: datetime, end: datetime) -> Iterator[datetime]:
        """Yields nonwork exceptions (i.e. holidays) between 2 dates."""
        if not isinstance(start, datetime) or not isinstance(end, datetime):
            raise ValueError("Arguments must be a datetime object")

        # Clean start and end dates to remove time values
        cl_dates = clean_dates(start, end)

        check_date = min(cl_dates)
        while check_date <= max(cl_dates):
            if self.holidays and check_date in self.holidays:
                yield check_date
            if (
                not self.holidays
                and self.base_calendar
                and check_date in self.base_calendar.holidays
            ):
                yield check_date
            check_date += timedelta(days=1)

    def iter_workdays(self, start: datetime, end: datetime) -> Iterator[datetime]:
        """Yields valid workdays between 2 dates"""

        if not isinstance(start, datetime) or not isinstance(end, datetime):
            raise ValueError("Arguments must be a datetime object")

        # Clean start and end dates to remove time values
        _dates = clean_dates(start, end)

        check_date = min(_dates)
        while check_date <= max(_dates):
            if self.is_workday(check_date):
                yield check_date
            check_date += timedelta(days=1)

    @cached_property
    def work_exceptions(self) -> dict[datetime, WeekDay]:
        """Parse work-day exceptions from Calendar data field."""
        exception_dict = {}
        for exception in _parse_clndr_data(self.data, ClndrRegEx.exceptions.value):
            _date = self.conv_excel_date(int(exception[:5]))
            _day = _parse_work_day(exception)

            # Verify exception object is different than standard weekday object
            if _day != self.work_week.get(_day.week_day):
                exception_dict[_date] = _day

        return exception_dict

    @cached_property
    def work_week(self) -> dict[str, WeekDay]:
        """Parse work week from Calendar data field."""
        return {
            WEEKDAYS[int(day[0]) - 1]: _parse_work_day(day)
            for day in _parse_clndr_data(self.data, ClndrRegEx.weekdays.value)
        }

    def _calc_work_hours(
        self, date_to_calc: datetime, start_time: time, end_time: time
    ) -> float:
        """
        Calculate the work hours for a given day based on a start time, end time,
        and work shifts apportioned for that day of the week.
        """
        work_day = self._get_workday(date_to_calc)

        # date is not a workday
        if not work_day:
            return 0.0

        # reassign times if they were passed in the wrong order
        start_time, end_time = min(start_time, end_time), max(start_time, end_time)

        # ensure start and end times do not fall outside the workhours for the Week Day
        start_time = max(start_time, work_day.start)
        end_time = min(end_time, work_day.finish)

        # date is a full day of work
        if start_time == work_day.start and end_time == work_day.finish:
            return round(work_day.hours, 3)

        day_work_hrs = work_day.hours

        for shift in work_day.shifts:
            # start time falls within this shift
            if shift[0] <= start_time < shift[1]:
                day_work_hrs -= calc_time_var_hrs(shift[0], start_time)

                # end time also falls within this shift
                if end_time < shift[1]:
                    day_work_hrs -= calc_time_var_hrs(end_time, shift[1])

                continue

            # only end time falls within this shift
            if shift[0] <= end_time <= shift[1]:
                day_work_hrs -= calc_time_var_hrs(end_time, shift[1])
                continue

            # neither start nor end time falls within this shift
            # deduct shift work hours from the day work hours
            day_work_hrs -= calc_time_var_hrs(shift[0], shift[1])

        return round(day_work_hrs, 3)

    def _get_workday(self, date: datetime) -> WeekDay:
        """Get the WeekDay object associated with a date."""
        clean_date = date.replace(microsecond=0, second=0, minute=0, hour=0)
        if clean_date in self.work_exceptions.keys():
            return self.work_exceptions[clean_date]

        return self.work_week[f"{clean_date:%A}"]


def _parse_clndr_data(clndr_data: str, reg_ex) -> list:
    """
    Searches Calendar data property and returns strings
    matching reg_ex argument.
    """
    return re.findall(reg_ex, clndr_data)


def _parse_work_day(day: str) -> WeekDay:
    """
    Parse WeekDay objects from string representing a work day.
    """
    weekday = WEEKDAYS[int(day[0]) - 1]
    shift_hours = sorted(
        [conv_time(hr) for hr in re.findall(ClndrRegEx.shift_hours.value, day)]
    )

    shift_hours_tuple: list[tuple[time, time]] = []
    for hr in range(0, len(shift_hours), 2):
        shift_hours_tuple.append((shift_hours[hr], shift_hours[hr + 1]))

    return WeekDay(weekday, shift_hours_tuple)
