import json
import uuid

from sqlalchemy.orm import Session

from app.graph.llm import invoke_json, world_context
from app.graph.state import SimulationState
from app.graph.utils import to_json
from app.models.event import Event
from app.prompts.loader import get_prompt_loader


def _fallback_events(ws: dict, tick_id: int) -> list[dict]:
    day = ws.get("current_day", 1)
    time = ws.get("current_time", "Morning")
    weather = ws.get("weather", "Clear")
    title = f"Village update on Day {day}"
    description = f"Villagers adjust their plans during {time.lower()} weather conditions ({weather})."
    return [
        {
            "event_id": f"evt_{tick_id}_{uuid.uuid4().hex[:8]}",
            "title": title,
            "category": "Economic",
            "description": description,
            "affected_agents": [],
            "importance": 0.4,
            "expected_consequences": ["Daily routines continue", "Small economic shifts"],
        }
    ]


def event_generator_node(state: SimulationState, db: Session) -> SimulationState:
    from app.config import get_settings

    loader = get_prompt_loader()
    settings = get_settings()
    ws = state.get("world_state", {})
    tick_id = state.get("tick_id", 0)
    if settings.simulation_fast_mode:
        slim = {
            "village_name": ws.get("village_name"),
            "current_day": ws.get("current_day"),
            "current_time": ws.get("current_time"),
            "weather": ws.get("weather"),
            "tick_id": ws.get("tick_id"),
            "active_plots": ws.get("active_plots"),
        }
        prompt = (
            loader.render("event_generator", world_state=to_json(slim))
            + "\n\nGenerate exactly 1 event only. Return valid JSON."
            + "\nUse no quotation marks inside string values."
        )
        temp = 0.25
    else:
        prompt = (
            world_context(max_chars=900)
            + "\n\n"
            + loader.render("event_generator", world_state=to_json(ws))
            + "\n\nGenerate 1-3 events only. Return valid JSON. Use no quotation marks inside string values."
        )
        temp = 0.3
    try:
        result = invoke_json(prompt, temperature=temp)
    except Exception as exc:
        fallback = _fallback_events(ws, tick_id)
        persisted: list[dict] = []
        for ev in fallback:
            row = Event(
                event_id=ev["event_id"],
                tick_id=tick_id,
                title=ev["title"],
                category=ev["category"],
                description=ev["description"],
                importance=float(ev["importance"]),
                affected_agents=json.dumps(ev.get("affected_agents", [])),
                expected_consequences=json.dumps(ev.get("expected_consequences", [])),
            )
            db.add(row)
            persisted.append(ev)
        db.flush()
        return {"events": persisted, "error": f"event_generator: {exc}"}

    events = result.get("events", [])
    persisted: list[dict] = []

    for ev in events:
        event_id = ev.get("event_id") or str(uuid.uuid4())[:8]
        row = Event(
            event_id=event_id,
            tick_id=tick_id,
            title=ev.get("title", "Village event"),
            category=ev.get("category", "Community"),
            description=ev.get("description"),
            importance=float(ev.get("importance", 0.5)),
            affected_agents=json.dumps(ev.get("affected_agents", [])),
            expected_consequences=json.dumps(ev.get("expected_consequences", [])),
        )
        db.add(row)
        ev["event_id"] = event_id
        persisted.append(ev)

    db.flush()
    return {"events": persisted}
