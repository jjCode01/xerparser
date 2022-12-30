from datetime import datetime, time


def calc_time_var_hrs(start: time, end: time, ordered: bool = False) -> float:
    """Calculate the variance in hours between two time objects

    Args:
        start (time): start time
        end (time): end time
        ordered (bool, optional): If False, reorder start and end times if start is greater than end. Defaults to False.

    Returns:
        float: Variance between two times in hours
    """

    if not all(isinstance(t, time) for t in [start, end]):
        raise ValueError("Value Error: Arguments must be a time object")

    if not ordered:
        # put dates in proper order so that the smaller date
        # is subtracted from the larger date.
        start, end = min(start, end), max(start, end)

    start_date = datetime.combine(datetime.today(), start)
    end_date = datetime.combine(datetime.today(), end)

    return round((end_date - start_date).total_seconds() / 3600, 2)


def clean_date(date: datetime) -> datetime:
    """Sets time value to 00:00:00 (12AM)"""
    if not isinstance(date, datetime):
        raise ValueError("Value Error: Argument must be a datetime object")

    return date.replace(microsecond=0, second=0, minute=0, hour=0)


def clean_dates(*dates: datetime) -> list[datetime]:
    """Remove time values from a list of datetime objects"""
    return [clean_date(d) for d in dates]


def conv_time(time_str: str) -> time:
    """Convert a string representing time into a datetime.time object."""
    return datetime.strptime(time_str, "%H:%M").time()
