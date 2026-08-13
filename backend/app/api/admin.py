from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.services.seed import run_seed

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/seed")
def admin_seed(reset: bool = True, db: Session = Depends(get_db)):
    return run_seed(db, reset=reset)
