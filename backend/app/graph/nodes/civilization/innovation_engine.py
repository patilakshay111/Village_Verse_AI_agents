from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.graph.llm import invoke_json
from app.graph.utils import to_json
from app.prompts.loader import get_prompt_loader
from app.config import get_settings


def civ_innovation_engine_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    if get_settings().simulation_fast_mode:
        return {"innovation_updates": {"innovation": "", "expected_impact": "", "implementation_cost": 0}}
    loader = get_prompt_loader()
    prompt = loader.load_raw("civilization/civilization_system_prompt") + "\n\n" + loader.load_raw(
        "civilization/innovation_engine"
    )
    prompt += "\n\nWORLD_STATE:\n" + to_json(state.get("world_state", {}))
    prompt += "\n\nACTIVE_PROJECTS:\n" + to_json(state.get("world_state", {}).get("active_projects", []))
    result = invoke_json(prompt, temperature=0.35)
    return {"innovation_updates": result}

