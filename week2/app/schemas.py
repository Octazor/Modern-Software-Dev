from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel


class NoteCreate(BaseModel):
    content: str


class NoteOut(BaseModel):
    id: int
    content: str
    created_at: str

    class Config:
        orm_mode = True


class ActionItemCreate(BaseModel):
    text: str
    note_id: Optional[int] = None


class ActionItemOut(BaseModel):
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: str

    class Config:
        orm_mode = True


class ExtractPayload(BaseModel):
    text: str
    save_note: bool = False


class ExtractResponse(BaseModel):
    note_id: Optional[int]
    items: List[ActionItemOut]
