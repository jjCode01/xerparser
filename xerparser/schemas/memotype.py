from pydantic import BaseModel


class MEMOTYPE(BaseModel):
    memo_type_id: str
    memo_type: str
