import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.schemas.villager import (
    MemoryResponse,
    RelationshipSummary,
    VillagerDetailResponse,
    VillagerResponse,
)
from app.services import queries

router = APIRouter(prefix="/villagers", tags=["villagers"])


@router.get("", response_model=list[VillagerResponse])
def list_villagers(
    family_id: str | None = None,
    location_id: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    rows, _ = queries.list_villagers(
        db, family_id=family_id, location_id=location_id, offset=offset, limit=limit
    )
    return rows


@router.get("/{villager_id}", response_model=VillagerDetailResponse)
def get_villager(villager_id: str, db: Session = Depends(get_db)):
    detail = queries.get_villager_detail(db, villager_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Villager not found")
    v = detail["villager"]
    return VillagerDetailResponse(
        id=v.id,
        name=v.name,
        age=v.age,
        gender=v.gender,
        occupation=v.occupation,
        family_id=v.family_id,
        location_id=v.location_id,
        current_emotion=v.current_emotion,
        emotion_intensity=v.emotion_intensity,
        education=v.education,
        personality=v.personality_list(),
        friends=[RelationshipSummary(**f) for f in detail["friends"]],
        rivals=[RelationshipSummary(**r) for r in detail["rivals"]],
        memories=[
            MemoryResponse(
                id=m.id,
                content=m.content,
                emotion=m.emotion,
                importance=m.importance,
                sim_timestamp=m.sim_timestamp,
            )
            for m in detail["memories"]
        ],
        recent_stories=detail["recent_stories"],
        agent_role=v.agent_role,
        cash=v.cash,
        bank_balance=v.bank_balance,
        monthly_income=v.monthly_income,
        monthly_expenses=v.monthly_expenses,
        net_worth=v.net_worth,
        reputation=v.reputation,
        skills=(json.loads(v.skills) if v.skills else []) if isinstance(v.skills, str) else [],
        intelligence=v.intelligence,
        employment_status=v.employment_status,
    )
