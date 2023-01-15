# xerparser
# actvtype.py


class ACTVTYPE:
    """
    A class representing Activity Codes Types

    ...

    Attributes
    ----------
    uid: str
        Unique ID [actv_code_type_id]
    max_length: int
        Max Code Length [actv_short_len]
    name: str
        Activity Code [actv_code_type]
    proj_id: str
        Foreign Key for PROJECT
    scope: str
        Activity Code Type Scope [actv_code_type_scope]
    seq_num: int | None
        Sort Order
    """

    def __init__(self, **data) -> None:
        self.uid: str = data["actv_code_type_id"]
        self.max_length: int = int(data["actv_short_len"])
        self.name: str = data["actv_code_type"]
        self.proj_id: str = data["proj_id"]
        self.scope: str = _check_scope(data["actv_code_type_scope"])
        self.seq_num: int | None = None if (seq := data["seq_num"]) == "" else int(seq)

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
