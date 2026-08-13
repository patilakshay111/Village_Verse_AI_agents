from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.services import queries

router = APIRouter(prefix="/locations", tags=["locations"])


class LocationResponse(BaseModel):
    id: str
    name: str
    description: str | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[LocationResponse])
def list_locations(db: Session = Depends(get_db)):
    return queries.list_locations(db)
