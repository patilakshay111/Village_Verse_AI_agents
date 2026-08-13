from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.models.story import Story
from app.schemas.story import StoryListResponse, StoryResponse
from app.services import queries

router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("", response_model=StoryListResponse)
def list_stories(
    date: str | None = None,
    time_from: str | None = None,
    time_to: str | None = None,
    category: str | None = None,
    villager_id: str | None = None,
    family_id: str | None = None,
    location: str | None = None,
    importance_min: float | None = Query(None, ge=0, le=1),
    q: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    rows, total = queries.list_stories(
        db,
        date=date,
        time_from=time_from,
        time_to=time_to,
        category=category,
        villager_id=villager_id,
        family_id=family_id,
        location=location,
        importance_min=importance_min,
        q=q,
        offset=offset,
        limit=limit,
    )
    return StoryListResponse(
        items=[StoryResponse.model_validate(s) for s in rows],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{story_id}", response_model=StoryResponse)
def get_story(story_id: str, db: Session = Depends(get_db)):
    row = db.query(Story).filter(Story.story_id == story_id).first()
    if not row:
        row = db.query(Story).filter(Story.id == int(story_id)).first() if story_id.isdigit() else None
    if not row:
        raise HTTPException(status_code=404, detail="Story not found")
    return StoryResponse.model_validate(row)
