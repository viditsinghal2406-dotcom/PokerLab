from pydantic import BaseModel


class HistoryItem(BaseModel):
    id: int
    kind: str
    name: str
    created_at: str


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
