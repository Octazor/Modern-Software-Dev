from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import db, models
from ..schemas import (
    ActionItemOut,
    ExtractPayload,
    ExtractResponse,
)
from ..services.extract import extract_action_items

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractPayload, db_session: Session = Depends(db.get_db)) -> ExtractResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: int | None = None
    if payload.save_note:
        note = models.Note(content=text)
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)
        note_id = note.id

    items_texts = extract_action_items(text)
    items: list[models.ActionItem] = []
    for t in items_texts:
        ai = models.ActionItem(text=t, note_id=note_id)
        db_session.add(ai)
        db_session.commit()
        db_session.refresh(ai)
        items.append(ai)

    return {"note_id": note_id, "items": items}


@router.get("", response_model=list[ActionItemOut])
def list_all(
    note_id: int | None = None, db_session: Session = Depends(db.get_db)
) -> list[models.ActionItem]:
    query = db_session.query(models.ActionItem)
    if note_id is not None:
        query = query.filter(models.ActionItem.note_id == note_id)
    return query.order_by(models.ActionItem.id.desc()).all()


@router.post("/{action_item_id}/done", response_model=ActionItemOut)
def mark_done(
    action_item_id: int,
    payload: dict[str, Any],
    db_session: Session = Depends(db.get_db),
) -> models.ActionItem:
    done = bool(payload.get("done", True))
    item = db_session.query(models.ActionItem).get(action_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="action item not found")
    item.done = done
    db_session.commit()
    db_session.refresh(item)
    return item
