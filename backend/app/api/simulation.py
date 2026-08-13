from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.schemas.simulation import RunSimulationRequest, SimulationStatusResponse
from app.services import simulation as sim_service

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/tick")
def simulation_tick(db: Session = Depends(get_db)):
    return sim_service.run_tick(db)


@router.post("/run")
def simulation_run(body: RunSimulationRequest, db: Session = Depends(get_db)):
    return sim_service.run_ticks(db, body.ticks)


@router.post("/start")
def simulation_start(db: Session = Depends(get_db)):
    return sim_service.start_continuous(db)


@router.post("/pause")
def simulation_pause(db: Session = Depends(get_db)):
    return sim_service.pause_simulation(db)


@router.get("/status", response_model=SimulationStatusResponse)
def simulation_status(db: Session = Depends(get_db)):
    return SimulationStatusResponse(**sim_service.get_status(db))
