from datetime import datetime

from sqlalchemy.orm import Session

from app.graph.state import SimulationState
from app.models.simulation_run import SimulationRun


def save_state_node(state: SimulationState, db: Session) -> SimulationState:
    sim = db.query(SimulationRun).order_by(SimulationRun.id.desc()).first()
    if not sim:
        sim = SimulationRun()
        db.add(sim)

    sim.current_day = state.get("current_day", sim.current_day)
    sim.current_time = state.get("current_time", sim.current_time)
    sim.tick_count = state.get("tick_id", sim.tick_count)
    sim.weather = state.get("weather", sim.weather)
    sim.last_tick_at = datetime.utcnow()

    if state.get("error"):
        sim.last_error = state["error"][:500]
    else:
        sim.last_error = None

    db.flush()
    return {}
