import json

from sqlalchemy.orm import Session

from app.graph.llm import invoke_json
from app.graph.state import SimulationState
from app.graph.utils import to_json
from app.models.memory import Memory
from app.prompts.loader import get_prompt_loader


def memory_node(state: SimulationState, db: Session) -> SimulationState:
    conversation = state.get("conversation", [])
    if not conversation:
        return {"new_memories": []}

    loader = get_prompt_loader()
    prompt = loader.render("memory_manager", conversation=to_json(conversation))

    try:
        result = invoke_json(prompt, temperature=0.3)
    except Exception as exc:
        return {"new_memories": [], "error": f"memory: {exc}"}

    new_memories = result.get("new_memories", [])
    tick_id = state.get("tick_id", 0)
    day = state.get("current_day", 1)
    time_slot = state.get("current_time", "Morning")
    timestamp = f"Day {day} {time_slot}"

    for mem in new_memories:
        row = Memory(
            agent_id=mem.get("agent_id", ""),
            content=mem.get("memory", ""),
            emotion=mem.get("emotion"),
            importance=float(mem.get("importance", 0.5)),
            participants=json.dumps(mem.get("participants", [])),
            sim_timestamp=mem.get("timestamp") or timestamp,
            tick_id=tick_id,
        )
        if row.agent_id and row.content:
            db.add(row)

    db.flush()
    return {"new_memories": new_memories}
