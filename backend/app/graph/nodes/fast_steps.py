"""Rule-based steps used in fast simulation mode (no extra LLM calls)."""

import json

from sqlalchemy.orm import Session

from app.graph.state import SimulationState
from app.graph.utils import clamp
from app.models.memory import Memory
from app.models.relationship import Relationship
from app.models.villager import Villager


def _name_to_id(state: SimulationState) -> dict[str, str]:
    return {
        a.get("name", ""): a["agent_id"]
        for a in state.get("selected_agents", [])
        if a.get("name")
    }


def memory_fast_node(state: SimulationState, db: Session) -> SimulationState:
    conversation = state.get("conversation", [])
    name_map = _name_to_id(state)
    tick_id = state.get("tick_id", 0)
    day = state.get("current_day", 1)
    time_slot = state.get("current_time", "Morning")
    timestamp = f"Day {day} {time_slot}"
    new_memories: list[dict] = []

    for line in conversation[:4]:
        speaker = line.get("speaker", "")
        message = line.get("message", "")
        if not message:
            continue
        agent_id = name_map.get(speaker)
        if not agent_id:
            continue
        row = Memory(
            agent_id=agent_id,
            content=message[:200],
            emotion=line.get("emotion"),
            importance=0.45,
            participants=json.dumps(list(name_map.keys())[:5]),
            sim_timestamp=timestamp,
            tick_id=tick_id,
        )
        db.add(row)
        new_memories.append(
            {"agent_id": agent_id, "memory": message[:200], "importance": 0.45}
        )

    db.flush()
    return {"new_memories": new_memories}


def relationship_fast_node(state: SimulationState, db: Session) -> SimulationState:
    """Light relationship nudge from conversation tone (no LLM)."""
    conversation = state.get("conversation", [])
    agents = state.get("selected_agents", [])
    if len(agents) < 2 or not conversation:
        return {"relationship_updates": []}

    negative = sum(
        1
        for c in conversation
        if any(w in (c.get("message") or "").lower() for w in ("no", "never", "angry", "wrong", "liar"))
    )
    ids = [a["agent_id"] for a in agents[:3]]
    updates = []
    for i, a in enumerate(ids):
        for b in ids[i + 1 :]:
            pair = sorted([a, b])
            row = (
                db.query(Relationship)
                .filter(
                    Relationship.agent_a_id == pair[0],
                    Relationship.agent_b_id == pair[1],
                )
                .first()
            )
            if not row:
                continue
            delta = -3 if negative >= 2 else 2
            row.friendship = clamp(row.friendship + delta)
            updates.append({"agent_a": pair[0], "agent_b": pair[1], "friendship_change": delta})

    db.flush()
    return {"relationship_updates": updates}


def emotion_fast_node(state: SimulationState, db: Session) -> SimulationState:
    conversation = state.get("conversation", [])
    name_map = _name_to_id(state)
    last_by_name: dict[str, dict] = {}
    for line in conversation:
        speaker = line.get("speaker", "")
        if speaker:
            last_by_name[speaker] = line

    updates = []
    for name, agent_id in name_map.items():
        villager = db.query(Villager).filter(Villager.id == agent_id).first()
        if not villager:
            continue
        line = last_by_name.get(name, {})
        emotion = line.get("emotion") or "Neutral"
        villager.current_emotion = emotion
        villager.emotion_intensity = 0.55 if emotion not in ("Neutral", "Calm") else 0.35
        updates.append({"agent_id": agent_id, "emotion": emotion, "intensity": villager.emotion_intensity})

    db.flush()
    return {"emotion_updates": updates}


def gossip_skip_node(state: SimulationState, db: Session) -> SimulationState:
    return {"rumors": [], "updated_rumors": []}
