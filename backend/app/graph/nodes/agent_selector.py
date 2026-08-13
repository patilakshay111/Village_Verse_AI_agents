import json
import random

from sqlalchemy.orm import Session

from app.config import get_settings
from app.graph.state import SimulationState
from app.models.location import Location
from app.models.villager import Villager
from app.services.village_plots import PLOT_CATEGORIES, plot_agent_ids


def _villager_dict(v: Villager, location_name: str | None) -> dict:
    return {
        "agent_id": v.id,
        "name": v.name,
        "age": v.age,
        "gender": v.gender,
        "occupation": v.occupation,
        "family_id": v.family_id,
        "personality_traits": v.personality_list(),
        "current_emotion": v.current_emotion,
        "location_id": v.location_id,
        "location_name": location_name,
    }


def agent_selector_node(state: SimulationState, db: Session) -> SimulationState:
    settings = get_settings()
    limit = settings.effective_agents_per_tick
    events = state.get("events", [])
    villagers = db.query(Villager).all()
    locations = {loc.id: loc.name for loc in db.query(Location).all()}

    affected_ids: set[str] = set()
    plot_categories: set[str] = set()
    for ev in events:
        cat = (ev.get("category") or "").strip()
        if cat in PLOT_CATEGORIES:
            plot_categories.add(cat)
        for aid in ev.get("affected_agents", []):
            if isinstance(aid, str):
                affected_ids.add(aid)

    plot_ids = plot_agent_ids(db) if plot_categories else set()
    if plot_categories & {"Romance"}:
        plot_ids |= {v.id for v in villagers if v.name in ("Priya Sharma", "Kiran Pawar")}
    if plot_categories & {"Daru", "Funny", "Conflict"}:
        liquor = db.query(Location).filter(Location.id == "country_liquor").first()
        if liquor:
            for v in villagers:
                if v.location_id == liquor.id and v.id not in plot_ids:
                    plot_ids.add(v.id)

    candidates = []
    if affected_ids:
        candidates = [v for v in villagers if v.id in affected_ids]
    if plot_ids:
        for v in villagers:
            if v.id in plot_ids and v not in candidates:
                candidates.append(v)

    if len(candidates) < limit:
        hub = db.query(Location).filter(Location.name == "Tea Stall").first()
        if hub:
            at_hub = [v for v in villagers if v.location_id == hub.id]
            for v in at_hub:
                if v not in candidates:
                    candidates.append(v)

    if len(candidates) < limit:
        pool = [v for v in villagers if v not in candidates]
        random.shuffle(pool)
        candidates.extend(pool[: limit - len(candidates)])

    selected = candidates[:limit]
    if not selected and villagers:
        selected = random.sample(villagers, min(limit, len(villagers)))

    primary = selected[0] if selected else None
    location = {"id": None, "name": "Main Chowk"}
    if primary and primary.location_id:
        location = {
            "id": primary.location_id,
            "name": locations.get(primary.location_id, "Main Chowk"),
        }

    agent_dicts = [
        _villager_dict(v, locations.get(v.location_id)) for v in selected
    ]

    return {
        "selected_agents": agent_dicts,
        "location": location,
    }
