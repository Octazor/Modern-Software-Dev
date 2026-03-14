from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import db, models
from ..schemas import NoteCreate, NoteOut

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteOut)
def create_note(payload: NoteCreate, db_session: Session = Depends(db.get_db)) -> models.Note:
    note = models.Note(content=payload.content)
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    return note


@router.get("", response_model=list[NoteOut])
def list_notes(db_session: Session = Depends(db.get_db)) -> list[models.Note]:
    return db_session.query(models.Note).order_by(models.Note.id.desc()).all()


@router.get("/{note_id}", response_model=NoteOut)
def get_single_note(note_id: int, db_session: Session = Depends(db.get_db)) -> models.Note:
    note = db_session.query(models.Note).get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="note not found")
    return note
