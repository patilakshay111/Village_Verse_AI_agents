from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.schemas.conversation import (
    ConversationListResponse,
    ConversationResponse,
    conversation_from_row,
)
from app.services import queries

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ConversationListResponse)
def list_conversations(
    tick_id: int | None = None,
    villager_id: str | None = None,
    location_id: str | None = None,
    q: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    rows, total = queries.list_conversations(
        db,
        tick_id=tick_id,
        villager_id=villager_id,
        location_id=location_id,
        q=q,
        offset=offset,
        limit=limit,
    )
    return ConversationListResponse(
        items=[conversation_from_row(conv, loc_name) for conv, loc_name in rows],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/by-tick/{tick_id}", response_model=ConversationResponse)
def get_conversation_by_tick(tick_id: int, db: Session = Depends(get_db)):
    row = queries.get_conversation_by_tick(db, tick_id)
    if not row:
        raise HTTPException(status_code=404, detail="Conversation not found for this tick")
    conv, loc_name = row
    return conversation_from_row(conv, loc_name)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    row = queries.get_conversation(db, conversation_id)
    if not row:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv, loc_name = row
    return conversation_from_row(conv, loc_name)
