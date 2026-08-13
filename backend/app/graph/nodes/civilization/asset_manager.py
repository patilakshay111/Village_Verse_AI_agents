from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.graph.llm import invoke_json
from app.graph.utils import to_json
from app.prompts.loader import get_prompt_loader
from app.config import get_settings


def civ_asset_manager_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    if get_settings().simulation_fast_mode:
        return {"asset_updates": {"asset_updates": []}}
    loader = get_prompt_loader()
    prompt = loader.load_raw("civilization/civilization_system_prompt") + "\n\n" + loader.load_raw(
        "civilization/asset_manager"
    )
    prompt += "\n\nWORLD_STATE:\n" + to_json(state.get("world_state", {}))
    prompt += "\n\nECONOMY_UPDATES:\n" + to_json(state.get("economy_updates", {}))
    result = invoke_json(prompt, temperature=0.3)
    return {"asset_updates": result}

