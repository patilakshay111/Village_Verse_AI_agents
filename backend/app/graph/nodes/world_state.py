import json
import random
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import get_settings
from app.graph.state import SimulationState
from app.models.simulation_run import SimulationRun
from app.models.villager import Villager

TIME_ORDER = ["Morning", "Afternoon", "Evening", "Night"]
WEATHER_OPTIONS = ["Clear", "Cloudy", "Hot", "Rainy", "Windy"]


def world_state_node(state: SimulationState, db: Session) -> SimulationState:
    sim = db.query(SimulationRun).order_by(SimulationRun.id.desc()).first()
    if not sim:
        sim = SimulationRun()
        db.add(sim)
        db.flush()

    tick_id = (sim.tick_count or 0) + 1
    current_time = sim.current_time or "Morning"
    current_day = sim.current_day or 1

    idx = TIME_ORDER.index(current_time) if current_time in TIME_ORDER else 0
    if idx < len(TIME_ORDER) - 1:
        current_time = TIME_ORDER[idx + 1]
    else:
        current_time = "Morning"
        current_day += 1

    if tick_id % 4 == 0:
        weather = random.choice(WEATHER_OPTIONS)
    else:
        weather = sim.weather or "Clear"

    villagers = db.query(Villager).all()
    location_map = {v.id: v.location_id for v in villagers if v.location_id}

    settings = get_settings()
    from app.services.village_plots import get_active_plots

    world_state = {
        "village_name": settings.village_name,
        "current_day": current_day,
        "current_time": current_time,
        "weather": weather,
        "population": len(villagers),
        "tick_id": tick_id,
        "location_map": location_map,
        "active_plots": get_active_plots(),
    }

    return {
        "tick_id": tick_id,
        "current_day": current_day,
        "current_time": current_time,
        "weather": weather,
        "world_state": world_state,
        "events": [],
        "selected_agents": [],
        "conversation": [],
        "new_memories": [],
        "relationship_updates": [],
        "emotion_updates": [],
        "rumors": [],
        "updated_rumors": [],
        "feed_entries": [],
        "error": None,
    }
