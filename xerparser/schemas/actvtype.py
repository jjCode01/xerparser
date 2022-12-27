# xerparser
# actvtype.py


class ACTVTYPE:
    """A class representing Activity Codes"""

    def __init__(self, **kwargs) -> None:
        self.uid: str = kwargs["actv_code_type_id"]
        self.max_length: int = int(kwargs["actv_short_len"])
        self.name: str = kwargs["actv_code_type"]
        self.proj_id: str = kwargs["proj_id"]
        self.scope: str = _check_scope(kwargs["actv_code_type_scope"])
        self.seq_num: int | None = (
            None if kwargs["seq_num"] == "" else int(kwargs["seq_num"])
        )

    def __eq__(self, __o: "ACTVTYPE") -> bool:
        return all(
            (
                self.max_length == __o.max_length,
                self.name == __o.name,
                self.scope == __o.scope,
            )
        )

    def __hash__(self) -> int:
        return hash((self.max_length, self.name, self.scope))


def _check_scope(value: str) -> str:
    if not value.startswith("AS_"):
        raise ValueError(f"Expected 'AS_Project' or 'AS_Global', got {value}")
    return value[3:]
