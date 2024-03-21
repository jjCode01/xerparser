# xerparser
# actvtype.py


class ACTVTYPE:
    """
    A class representing Activity Codes Types
    """

    def __init__(self, **data: str) -> None:
        self.uid: str = data["actv_code_type_id"]
        """Unique Table ID"""
        self.max_length: int = int(data["actv_short_len"])
        """Max Character Length of Acticity Code"""
        self.name: str = data["actv_code_type"]
        """Name of Activity Code Type"""
        self.proj_id: str = data["proj_id"]
        """Foreign Key for Project (Project Level Activity Codes)"""
        self.scope: str = _check_scope(data["actv_code_type_scope"])
        """Activity Code Scope - Global, Enterpise, or Project"""
        self.seq_num: int | None = None if (seq := data["seq_num"]) == "" else int(seq)
        """Sort Order"""

    def __eq__(self, __o: "ACTVTYPE") -> bool:
        return all(
            (
                self.max_length == __o.max_length,
                self.name == __o.name,
                self.scope == __o.scope,
            )
        )

    def __gt__(self, __o: "ACTVTYPE") -> bool:
        return self.name > __o.name

    def __lt__(self, __o: "ACTVTYPE") -> bool:
        return self.name < __o.name

    def __hash__(self) -> int:
        return hash((self.max_length, self.name, self.scope))


def _check_scope(value: str) -> str:
    if not value.startswith("AS_"):
        raise ValueError(f"Expected 'AS_Project' or 'AS_Global', got {value}")
    return value[3:]
