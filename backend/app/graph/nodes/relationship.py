import json

from sqlalchemy.orm import Session

from app.graph.llm import invoke_json
from app.graph.state import SimulationState
from app.graph.utils import clamp, to_json
from app.models.relationship import Relationship
from app.prompts.loader import get_prompt_loader


def _get_or_create(db: Session, a: str, b: str) -> Relationship:
    pair = sorted([a, b])
    row = (
        db.query(Relationship)
        .filter(
            Relationship.agent_a_id == pair[0],
            Relationship.agent_b_id == pair[1],
        )
        .first()
    )
    if row:
        return row
    row = Relationship(agent_a_id=pair[0], agent_b_id=pair[1])
    db.add(row)
    db.flush()
    return row


def relationship_node(state: SimulationState, db: Session) -> SimulationState:
    conversation = state.get("conversation", [])
    if not conversation:
        return {"relationship_updates": []}

    agent_ids = [a["agent_id"] for a in state.get("selected_agents", [])]
    rel_state = []
    if len(agent_ids) >= 2:
        for i, a in enumerate(agent_ids):
            for b in agent_ids[i + 1 :]:
                row = _get_or_create(db, a, b)
                rel_state.append(
                    {
                        "agent_a": row.agent_a_id,
                        "agent_b": row.agent_b_id,
                        "friendship": row.friendship,
                        "trust": row.trust,
                        "respect": row.respect,
                        "rivalry": row.rivalry,
                    }
                )

    loader = get_prompt_loader()
    prompt = loader.render(
        "relationship_manager",
        conversation=to_json(conversation),
        relationship_state=to_json(rel_state),
    )

    try:
        result = invoke_json(prompt, temperature=0.3)
    except Exception as exc:
        return {"relationship_updates": [], "error": f"relationship: {exc}"}

    updates = result.get("updates", [])
    for upd in updates:
        a = upd.get("agent_a")
        b = upd.get("agent_b")
        if not a or not b:
            continue
        row = _get_or_create(db, a, b)
        row.friendship = clamp(row.friendship + float(upd.get("friendship_change", 0)))
        row.trust = clamp(row.trust + float(upd.get("trust_change", 0)))
        row.respect = clamp(row.respect + float(upd.get("respect_change", 0)))
        row.rivalry = clamp(row.rivalry + float(upd.get("rivalry_change", 0)))
        row.last_reason = upd.get("reason")

    db.flush()
    return {"relationship_updates": updates}
