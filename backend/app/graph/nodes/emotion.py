import json

from sqlalchemy.orm import Session

from app.graph.llm import invoke_json
from app.graph.state import SimulationState
from app.graph.utils import to_json
from app.models.memory import Memory
from app.models.villager import Villager
from app.prompts.loader import get_prompt_loader


def _apply_emotion(
    db: Session, agent_id: str, emotion: str, intensity: float
) -> dict | None:
    villager = db.query(Villager).filter(Villager.id == agent_id).first()
    if not villager:
        return None
    villager.current_emotion = emotion
    villager.emotion_intensity = intensity
    return {"agent_id": agent_id, "emotion": emotion, "intensity": intensity}


def emotion_node(state: SimulationState, db: Session) -> SimulationState:
    conversation = state.get("conversation", [])
    agents = state.get("selected_agents", [])
    if not conversation or not agents:
        return {"emotion_updates": []}

    updates: list[dict] = []
    agent_ids = [a["agent_id"] for a in agents]
    recent_by_agent: dict[str, list] = {}
    for aid in agent_ids:
        rows = (
            db.query(Memory)
            .filter(Memory.agent_id == aid)
            .order_by(Memory.importance.desc())
            .limit(2)
            .all()
        )
        recent_by_agent[aid] = [{"memory": m.content, "emotion": m.emotion} for m in rows]

    # One LLM call for all agents (was N calls — very slow on small models)
    batch_prompt = (
        "You are the Emotion Engine. For EACH agent below, set emotion and intensity (0-1).\n"
        'Return JSON only: {"updates":[{"agent_id":"","emotion":"","intensity":0.5,"reason":""}]}\n\n'
        f"Agents:\n{to_json(agents)}\n\n"
        f"Conversation:\n{to_json(conversation)}\n\n"
        f"Recent memories:\n{to_json(recent_by_agent)}"
    )

    try:
        result = invoke_json(batch_prompt, temperature=0.35)
        for upd in result.get("updates", []):
            aid = upd.get("agent_id")
            if not aid:
                continue
            applied = _apply_emotion(
                db,
                aid,
                upd.get("emotion", "Neutral"),
                float(upd.get("intensity", 0.5)),
            )
            if applied:
                applied["reason"] = upd.get("reason")
                updates.append(applied)
    except Exception:
        loader = get_prompt_loader()
        for agent in agents:
            aid = agent["agent_id"]
            villager = db.query(Villager).filter(Villager.id == aid).first()
            if not villager:
                continue
            try:
                result = invoke_json(
                    loader.render(
                        "emotion_engine",
                        agent=to_json(agent),
                        conversation=to_json(conversation),
                        recent_memories=to_json(recent_by_agent.get(aid, [])),
                        current_emotion=villager.current_emotion,
                    ),
                    temperature=0.4,
                )
                applied = _apply_emotion(
                    db,
                    aid,
                    result.get("emotion", villager.current_emotion),
                    float(result.get("intensity", 0.5)),
                )
                if applied:
                    updates.append(applied)
            except Exception:
                continue

    db.flush()
    return {"emotion_updates": updates}
