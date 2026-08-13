import json
import uuid

from sqlalchemy.orm import Session

from app.graph.llm import invoke_json, world_context
from app.graph.state import SimulationState
from app.graph.utils import to_json
from app.models.conversation import Conversation
from app.models.memory import Memory
from app.models.relationship import Relationship
from app.models.villager import Villager
from app.prompts.loader import get_prompt_loader
from app.schemas.story import coerce_string_list


def _allowed_names(agents: list[dict]) -> list[str]:
    return [a["name"] for a in agents if a.get("name")]


def _normalize_speaker(speaker: str, allowed: list[str]) -> str:
    """Map LLM speaker labels to one of the participants actually in the scene."""
    if not allowed:
        return speaker
    if speaker in allowed:
        return speaker

    raw = (speaker or "").strip()
    low = raw.lower()
    for name in allowed:
        if name.lower() == low:
            return name

    for name in allowed:
        parts = name.lower().split()
        if any(part in low for part in parts) or any(part in parts for part in low.split()):
            return name

    for name in allowed:
        if name.split()[0].lower() == low.split()[0].lower():
            return name

    return allowed[0]


def _sanitize_conversation(conversation: list, agents: list[dict]) -> list[dict]:
    """Ensure every line is spoken by a selected villager; fix common small-model swaps."""
    allowed = _allowed_names(agents)
    if not allowed:
        return []

    cleaned: list[dict] = []
    last_speaker: str | None = None
    for raw in conversation:
        if not isinstance(raw, dict):
            continue
        message = str(raw.get("message") or raw.get("text") or "").strip()
        if not message:
            continue

        speaker = _normalize_speaker(str(raw.get("speaker") or ""), allowed)
        msg_low = message.lower()

        # First-person reply after "you ..." should be the other person, not a third party.
        if last_speaker and cleaned:
            prev_msg = cleaned[-1].get("message", "").lower()
            if ("you " in prev_msg or "tum " in prev_msg or "tumhe " in prev_msg) and (
                msg_low.startswith("i'm ") or msg_low.startswith("i am ") or msg_low.startswith("main ")
            ):
                others = [n for n in allowed if n != last_speaker]
                if speaker == last_speaker and others:
                    speaker = others[0]

        emotion = raw.get("emotion")
        cleaned.append(
            {
                "speaker": speaker,
                "message": message,
                "emotion": str(emotion).strip() if emotion else None,
            }
        )
        last_speaker = speaker

    return cleaned


def _sanitize_moments(moments: list, allowed: list[str], location_name: str) -> list[str]:
    texts = coerce_string_list(moments)
    loc = location_name or "the village"
    out: list[str] = []
    for text in texts:
        if not any(name.split()[0] in text for name in allowed) and len(allowed) > 0:
            text = f"{allowed[0]} and others at {loc}: {text}"
        out.append(text[:240])
    return out[:3]


def _fallback_conversation(agents: list[dict], event: dict, location_name: str) -> tuple[list[dict], list[str]]:
    names = _allowed_names(agents)
    if not names:
        return [], []

    first = names[0]
    second = names[1] if len(names) > 1 else names[0]
    third = names[2] if len(names) > 2 else second
    event_title = str(event.get("title") or "the situation").strip()
    location_label = location_name or "the village"

    conversation = [
        {
            "speaker": first,
            "message": f"Looks like {event_title.lower()} at {location_label}. We need to handle this carefully.",
            "emotion": "Concerned",
        },
        {
            "speaker": second,
            "message": "Yes, but we cannot keep talking. Somebody has to act now.",
            "emotion": "Serious",
        },
        {
            "speaker": third,
            "message": "Let us settle it properly and avoid making the whole village angry.",
            "emotion": "Calm",
        },
    ]
    moments = [f"{first}, {second}, and {third} discussed {event_title.lower()} at {location_label}"]
    return conversation, moments


def _load_relationships(db: Session, agent_ids: list[str]) -> list[dict]:
    if len(agent_ids) < 2:
        return []
    rows = (
        db.query(Relationship)
        .filter(
            Relationship.agent_a_id.in_(agent_ids),
            Relationship.agent_b_id.in_(agent_ids),
        )
        .all()
    )
    return [
        {
            "agent_a": r.agent_a_id,
            "agent_b": r.agent_b_id,
            "friendship": r.friendship,
            "trust": r.trust,
            "respect": r.respect,
            "rivalry": r.rivalry,
        }
        for r in rows
    ]


def _load_memories(db: Session, agent_ids: list[str], limit: int = 5) -> list[dict]:
    rows = (
        db.query(Memory)
        .filter(Memory.agent_id.in_(agent_ids))
        .order_by(Memory.importance.desc())
        .limit(limit * len(agent_ids))
        .all()
    )
    out = []
    for m in rows:
        holder = db.query(Villager).filter(Villager.id == m.agent_id).first()
        out.append(
            {
                "holder_name": holder.name if holder else m.agent_id,
                "agent_id": m.agent_id,
                "memory": m.content,
                "importance": m.importance,
                "emotion": m.emotion,
            }
        )
    return out


def conversation_node(state: SimulationState, db: Session) -> SimulationState:
    agents = state.get("selected_agents", [])
    if not agents:
        return {"conversation": [], "important_moments": []}

    agent_ids = [a["agent_id"] for a in agents]
    event = state.get("events", [{}])[0] if state.get("events") else {}
    loc = state.get("location", {})
    loc_name = loc.get("name", "Village")
    from app.config import get_settings

    loader = get_prompt_loader()
    settings = get_settings()
    mem_limit = 2 if settings.simulation_fast_mode else 5
    body = loader.render(
        "conversation_engine",
        selected_agents=to_json(agents),
        location=to_json(state.get("location", {})),
        event=to_json(event),
        relationships=to_json(_load_relationships(db, agent_ids)),
        memories=to_json(_load_memories(db, agent_ids, limit=mem_limit)),
    )
    names = _allowed_names(agents)
    names_rule = (
        "\n\nALLOWED SPEAKER NAMES (use ONLY these exact strings in \"speaker\"): "
        + json.dumps(names, ensure_ascii=False)
        + "\nAnyone not in this list is ABSENT — mention them in third person only, never as speaker."
    )
    if settings.simulation_fast_mode:
        prompt = body + names_rule + "\n\nKeep conversation to 4-6 short lines. Return valid JSON only."
        temp = 0.35
    else:
        prompt = world_context(max_chars=600) + "\n\n" + body + names_rule + "\n\nKeep conversation to 4-6 short lines. Return valid JSON only."
        temp = 0.3

    try:
        result = invoke_json(prompt, temperature=temp)
    except Exception as exc:
        conversation, important_moments = _fallback_conversation(agents, event, loc_name)
        row = Conversation(
            tick_id=state.get("tick_id", 0),
            location_id=loc.get("id"),
            event_id=event.get("event_id"),
            transcript=json.dumps(conversation),
            participants=json.dumps([a.get("name", a.get("agent_id")) for a in agents]),
            important_moments=json.dumps(important_moments),
        )
        db.add(row)
        db.flush()
        return {
            "conversation": conversation,
            "important_moments": important_moments,
            "error": f"conversation: {exc}",
        }

    conversation = _sanitize_conversation(result.get("conversation", []), agents)
    important_moments = _sanitize_moments(result.get("important_moments", []), names, loc_name)

    row = Conversation(
        tick_id=state.get("tick_id", 0),
        location_id=loc.get("id"),
        event_id=event.get("event_id"),
        transcript=json.dumps(conversation),
        participants=json.dumps([a.get("name", a.get("agent_id")) for a in agents]),
        important_moments=json.dumps(important_moments),
    )
    db.add(row)
    db.flush()

    return {
        "conversation": conversation,
        "important_moments": important_moments,
    }
