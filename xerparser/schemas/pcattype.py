# xerparser
# pcattype.py


class PCATTYPE:
    """
    A class representing Project Code Types

    ...

    Attributes
    ----------
    uid: str
        Unique ID [proj_catg_type_id]
    max_length: int
        Max Code Length [proj_catg_short_len]
    name: str
        Activity Code [proj_catg_type]
    seq_num: int | None
        Sort Order
    """

    def __init__(self, **data) -> None:
        self.uid: str = data["proj_catg_type_id"]
        self.max_length: int = int(data["proj_catg_short_len"])
        self.name: str = data["proj_catg_type"]
        self.seq_num: int | None = None if (seq := data["seq_num"]) == "" else int(seq)

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
