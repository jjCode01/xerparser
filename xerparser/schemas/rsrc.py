from pydantic import BaseModel


class RSRC(BaseModel):
    """
    A class to represent a Resource.
    """

    rsrc_id: str
    clndr_id: str
    rsrc_name: str
    rsrc_short_name: str
    cost_qty_type: str
    active_flag: str
    rsrc_type: str

    def __eq__(self, __o: "RSRC") -> bool:
        return all(
            (
                self.rsrc_name == __o.rsrc_name,
                self.rsrc_short_name == __o.rsrc_short_name,
                self.rsrc_type == __o.rsrc_type,
            )
        )

    def __hash__(self) -> int:
        return hash((self.rsrc_name, self.rsrc_short_name, self.rsrc_type))
