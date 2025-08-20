# xerparser
# pcattype.py

from xerparser.src.validators import optional_int


class PCATTYPE:
    """
    A class representing Project Code Types
    """

    def __init__(self, **data: str) -> None:
        self.uid: str = data["proj_catg_type_id"]
        """Unique Table ID"""
        self.max_length: int = int(data["proj_catg_short_len"])
        """Max Character Length"""
        self.name: str = data["proj_catg_type"]
        """Project Code Name"""
        self.seq_num: int | None = optional_int(data["seq_num"])
        """Sort Order"""

    def __eq__(self, __o: "PCATTYPE") -> bool:
        return all(
            (
                self.max_length == __o.max_length,
                self.name == __o.name,
            )
        )

    def __gt__(self, __o: "PCATTYPE") -> bool:
        return self.name > __o.name

    def __lt__(self, __o: "PCATTYPE") -> bool:
        return self.name < __o.name

    def __hash__(self) -> int:
        return hash((self.max_length, self.name))
