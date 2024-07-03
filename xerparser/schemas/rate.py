from datetime import datetime

from xerparser.src.validators import date_format, float_or_zero


class Rate:
    """Units per Time Limits"""

    def __init__(self, **data: str) -> None:
        self.cost_per_qty: float = float_or_zero(data["cost_per_qty"])
        """Standard Rate"""
        self.cost_per_qty2: float = float_or_zero(data["cost_per_qty2"])
        """Internal Rate"""
        self.cost_per_qty3: float = float_or_zero(data["cost_per_qty3"])
        """External Rate"""
        self.cost_per_qty4: float = float_or_zero(data["cost_per_qty4"])
        """Price per Unit 4"""
        self.cost_per_qty5: float = float_or_zero(data["cost_per_qty5"])
        """Price per Unit 5"""
        self.max_qty_per_hr: float = float(data["max_qty_per_hr"].replace(",", "."))
        """Max Units per Time"""
        self.start_date: datetime = datetime.strptime(data["start_date"], date_format)
        """Effective Date"""

    def __eq__(self, __other: "Rate") -> bool:
        return self.start_date == __other.start_date

    def __gt__(self, __other: "Rate") -> bool:
        return self.start_date > __other.start_date

    def __hash__(self) -> int:
        return hash(self.start_date)

    def __lt__(self, __other: "Rate") -> bool:
        return self.start_date < __other.start_date
