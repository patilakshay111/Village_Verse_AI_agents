from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.graph.llm import invoke_json
from app.graph.utils import to_json
from app.prompts.loader import get_prompt_loader
from app.config import get_settings


def civ_software_company_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    if get_settings().simulation_fast_mode:
        return {"software_updates": {"product_name": "", "category": "", "problem_solved": "", "mvp_features": [], "revenue_model": "", "estimated_cost": 0}}
    loader = get_prompt_loader()
    prompt = loader.load_raw("civilization/civilization_system_prompt") + "\n\n" + loader.load_raw(
        "civilization/software_company_engine"
    )
    prompt += "\n\nWORLD_STATE:\n" + to_json(state.get("world_state", {}))
    prompt += "\n\nORGANIZATION_UPDATES:\n" + to_json(state.get("organization_updates", {}))
    result = invoke_json(prompt, temperature=0.4)
    return {"software_updates": result}

