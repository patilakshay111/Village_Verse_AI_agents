from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.graph.llm import invoke_json
from app.graph.utils import to_json
from app.prompts.loader import get_prompt_loader
from app.config import get_settings


def civ_organization_engine_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    if get_settings().simulation_fast_mode:
        return {"organization_updates": {"organization_type": "", "founders": [], "budget": 0}}
    loader = get_prompt_loader()
    prompt = loader.load_raw("civilization/civilization_system_prompt") + "\n\n" + loader.load_raw(
        "civilization/organization_engine"
    )
    prompt += "\n\nWORLD_STATE:\n" + to_json(state.get("world_state", {}))
    prompt += "\n\nINNOVATION:\n" + to_json(state.get("innovation_updates", {}))
    result = invoke_json(prompt, temperature=0.35)
    return {"organization_updates": result}

