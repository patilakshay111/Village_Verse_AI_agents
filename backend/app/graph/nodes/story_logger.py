import json
import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.config import get_settings
from app.graph.llm import invoke_json
from app.graph.state import SimulationState
from app.graph.utils import to_json
from app.schemas.story import coerce_string_list
from app.models.story import Story
from app.prompts.loader import get_prompt_loader

logger = logging.getLogger(__name__)


def _fallback_feed_entries(state: SimulationState, current_date: str, current_time: str) -> list[dict]:
    """Build minimal stories when LLM JSON fails (common on small models)."""
    location = state.get("location", {}).get("name", "Village")
    participants = [a.get("name", "") for a in state.get("selected_agents", []) if a.get("name")]
    entries: list[dict] = []

    for ev in state.get("events", [])[:2]:
        title = ev.get("title") or "Village event"
        entries.append(
            {
                "story_id": str(uuid.uuid4())[:8],
                "title": title,
                "summary": ev.get("description") or f"Something happened at {location}.",
                "full_story": ev.get("description") or title,
                "date": current_date,
                "time": current_time,
                "location": location,
                "category": ev.get("category") or "Community",
                "importance": float(ev.get("importance", 0.5)),
                "participants": participants,
                "families": [],
                "tags": [ev.get("category", "Village")] if ev.get("category") else [],
                "keywords": [],
                "future_hooks": [],
            }
        )

    convo = state.get("conversation", [])
    if convo and not entries:
        lines = [
            f'{c.get("speaker", "Someone")}: {c.get("message", "")}'
            for c in convo[:6]
            if c.get("message")
        ]
        summary = " ".join(lines)[:280] if lines else "Villagers talked at the gathering place."
        entries.append(
            {
                "story_id": str(uuid.uuid4())[:8],
                "title": f"Conversation at {location}",
                "summary": summary,
                "full_story": "\n".join(lines) if lines else summary,
                "date": current_date,
                "time": current_time,
                "location": location,
                "category": "Community",
                "importance": 0.45,
                "participants": participants,
                "families": [],
                "tags": ["Conversation"],
                "keywords": [location],
                "future_hooks": [],
            }
        )

    return entries


def story_logger_node(state: SimulationState, db: Session) -> SimulationState:
    loader = get_prompt_loader()
    settings = get_settings()
    now = datetime.now()
    current_date = f"Day {state.get('current_day', 1)}"
    current_time = state.get("current_time", "Morning")

    # Shorter prompt — small models struggle with huge world_prompt + JSON schema
    prompt = loader.render(
        "story_logger",
        current_date=current_date,
        current_time=current_time,
        events=to_json(state.get("events", [])),
        conversations=to_json(state.get("conversation", [])),
        relationship_changes=to_json(state.get("relationship_updates", [])),
        memory_updates=to_json(state.get("new_memories", [])),
        location=state.get("location", {}).get("name", settings.village_name),
        participants=to_json(
            [a.get("name") for a in state.get("selected_agents", [])]
        ),
    )

    try:
        result = invoke_json(prompt, temperature=0.35)
        entries = result.get("feed_entries", [])
        if not entries and isinstance(result.get("stories"), list):
            entries = result["stories"]
    except Exception as exc:
        logger.warning("story_logger LLM failed, using fallback: %s", exc)
        entries = _fallback_feed_entries(state, current_date, current_time)
        if not entries:
            return {"feed_entries": [], "error": f"story_logger: {exc}"}
    tick_id = state.get("tick_id", 0)

    for raw in entries:
        entry = dict(raw)
        entry["participants"] = coerce_string_list(entry.get("participants"))
        entry["families"] = coerce_string_list(entry.get("families"))
        entry["tags"] = coerce_string_list(entry.get("tags"))
        entry["keywords"] = coerce_string_list(entry.get("keywords"))
        entry["future_hooks"] = coerce_string_list(entry.get("future_hooks"))

        story_id = entry.get("story_id") or str(uuid.uuid4())[:8]
        if db.query(Story).filter(Story.story_id == story_id).first():
            story_id = f"{story_id}_{tick_id}_{uuid.uuid4().hex[:6]}"
        row = Story(
            story_id=story_id,
            tick_id=tick_id,
            title=entry.get("title", "Village story"),
            summary=entry.get("summary", ""),
            full_story=entry.get("full_story"),
            date=entry.get("date") or current_date,
            time=entry.get("time") or current_time,
            location=entry.get("location"),
            category=entry.get("category"),
            importance=float(entry.get("importance", 0.5)),
            participants=json.dumps(entry.get("participants", [])),
            families=json.dumps(entry.get("families", [])),
            tags=json.dumps(entry.get("tags", [])),
            keywords=json.dumps(entry.get("keywords", [])),
            relationship_changes=json.dumps(entry.get("relationship_changes", [])),
            future_hooks=json.dumps(entry.get("future_hooks", [])),
            related_story_ids=json.dumps(entry.get("related_story_ids", [])),
        )
        db.add(row)

    db.flush()
    return {"feed_entries": entries}
