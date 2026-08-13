import json
import uuid

from sqlalchemy.orm import Session

from app.graph.llm import invoke_json
from app.graph.state import SimulationState
from app.graph.utils import to_json
from app.models.rumor import Rumor
from app.prompts.loader import get_prompt_loader


def gossip_node(state: SimulationState, db: Session) -> SimulationState:
    loader = get_prompt_loader()
    existing = db.query(Rumor).order_by(Rumor.id.desc()).limit(10).all()
    existing_data = [
        {
            "rumor_id": r.rumor_id,
            "content": r.content,
            "spread_count": r.spread_count,
            "truth_level": r.truth_level,
        }
        for r in existing
    ]

    prompt = loader.render(
        "gossip_engine",
        conversations=to_json(state.get("conversation", [])),
        events=to_json(state.get("events", [])),
        existing_rumors=to_json(existing_data),
        active_agents=to_json(state.get("selected_agents", [])),
    )

    try:
        result = invoke_json(prompt, temperature=0.6)
    except Exception as exc:
        return {"rumors": [], "updated_rumors": [], "error": f"gossip: {exc}"}

    tick_id = state.get("tick_id", 0)
    new_rumors = result.get("rumors", [])
    updated = result.get("updated_rumors", [])

    for rumor in new_rumors:
        rid = rumor.get("rumor_id") or str(uuid.uuid4())[:8]
        if db.query(Rumor).filter(Rumor.rumor_id == rid).first():
            rid = f"{rid}_{tick_id}_{uuid.uuid4().hex[:6]}"
        row = Rumor(
            rumor_id=rid,
            content=rumor.get("content", ""),
            source_agent_id=rumor.get("source_agent_id"),
            heard_by=json.dumps(rumor.get("spread_to_agents", [])),
            truth_level=float(rumor.get("truth_level", 0.7)),
            distortion_level=float(rumor.get("distortion_level", 0.1)),
            spread_count=len(rumor.get("spread_to_agents", [])) or 1,
            importance=float(rumor.get("importance", 0.4)),
            related_event_id=rumor.get("related_event_id"),
            tick_id=tick_id,
        )
        db.add(row)

    for upd in updated:
        row = db.query(Rumor).filter(Rumor.rumor_id == upd.get("rumor_id")).first()
        if not row:
            continue
        heard = json.loads(row.heard_by or "[]")
        for agent_id in upd.get("spread_to_agents", []):
            if agent_id not in heard:
                heard.append(agent_id)
        row.heard_by = json.dumps(heard)
        row.spread_count += int(upd.get("spread_count_delta", 0))
        row.distortion_level = min(
            1.0,
            row.distortion_level + float(upd.get("distortion_level_delta", 0)),
        )

    db.flush()
    return {"rumors": new_rumors, "updated_rumors": updated}
