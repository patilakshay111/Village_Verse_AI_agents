from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.graph.llm import invoke_json
from app.graph.utils import to_json
from app.prompts.loader import get_prompt_loader
from app.config import get_settings


def civ_evolution_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    if get_settings().simulation_fast_mode:
        return {"evolution": {"current_stage": "", "next_stage": "", "requirements": []}}
    loader = get_prompt_loader()
    prompt = loader.load_raw("civilization/civilization_system_prompt") + "\n\n" + loader.load_raw(
        "civilization/civilization_evolution"
    )
    prompt += "\n\nWORLD_STATE:\n" + to_json(state.get("world_state", {}))
    prompt += "\n\nECONOMY:\n" + to_json(state.get("economy_updates", {}))
    prompt += "\n\nBUSINESS:\n" + to_json(state.get("business_updates", {}))
    prompt += "\n\nAI_WORKERS:\n" + to_json(state.get("ai_worker_updates", {}))
    result = invoke_json(prompt, temperature=0.3)
    return {"evolution": result}

