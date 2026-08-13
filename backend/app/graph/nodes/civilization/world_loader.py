from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.world.loader import WorldStateLoader


def civ_world_loader_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    """Load the WorldState snapshot (no LLM)."""
    ws = WorldStateLoader(db).load(
        tick_id=state.get("tick_id"),
        selected_agent_ids=[],
    )
    data = ws.to_dict()
    return {
        "world_state": data,
        "tick_id": data.get("tick_id"),
        # Use state-provided time for the current tick; SimulationRun will be updated later.
        "current_day": state.get("current_day") or data.get("current_day"),
        "current_time": state.get("current_time") or data.get("current_time"),
        "weather": state.get("weather") or data.get("weather"),
    }

