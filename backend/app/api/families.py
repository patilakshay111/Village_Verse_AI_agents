import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.services import queries

router = APIRouter(prefix="/families", tags=["families"])


class FamilyResponse(BaseModel):
    id: str
    name: str
    surname: str
    reputation: float
    wealth: float
    influence: float

    model_config = {"from_attributes": True}


class FamilyDetailResponse(FamilyResponse):
    members: list[dict[str, Any]] = []
    traditions: list[str] = []


@router.get("", response_model=list[FamilyResponse])
def list_families(db: Session = Depends(get_db)):
    return queries.list_families(db)


@router.get("/{family_id}", response_model=FamilyDetailResponse)
def get_family(family_id: str, db: Session = Depends(get_db)):
    detail = queries.get_family_detail(db, family_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Family not found")
    f = detail["family"]
    traditions = []
    if f.traditions:
        try:
            traditions = json.loads(f.traditions)
        except json.JSONDecodeError:
            traditions = [f.traditions]
    return FamilyDetailResponse(
        id=f.id,
        name=f.name,
        surname=f.surname,
        reputation=f.reputation,
        wealth=f.wealth,
        influence=f.influence,
        traditions=traditions if isinstance(traditions, list) else [],
        members=[
            {
                "id": m.id,
                "name": m.name,
                "age": m.age,
                "occupation": m.occupation,
                "current_emotion": m.current_emotion,
            }
            for m in detail["members"]
        ],
    )
