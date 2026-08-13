from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.graph.llm import invoke_json
from app.graph.utils import to_json
from app.prompts.loader import get_prompt_loader
from app.config import get_settings


def civ_ai_worker_factory_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    if get_settings().simulation_fast_mode:
        return {"ai_worker_updates": {"worker_type": "", "responsibilities": [], "estimated_value": 0}}
    loader = get_prompt_loader()
    prompt = loader.load_raw("civilization/civilization_system_prompt") + "\n\n" + loader.load_raw(
        "civilization/ai_worker_factory"
    )
    prompt += "\n\nWORLD_STATE:\n" + to_json(state.get("world_state", {}))
    prompt += "\n\nSOFTWARE_UPDATES:\n" + to_json(state.get("software_updates", {}))
    result = invoke_json(prompt, temperature=0.35)
    return {"ai_worker_updates": result}

