from sqlalchemy.orm import Session

from app.graph.civilization_state import CivilizationSimulationState
from app.graph.llm import invoke_json
from app.graph.utils import to_json
from app.prompts.loader import get_prompt_loader
from app.config import get_settings


def civ_economy_engine_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    if get_settings().simulation_fast_mode:
        return {"economy_updates": {"market_changes": [], "asset_price_updates": [], "economic_events": []}}
    loader = get_prompt_loader()
    world_state = state.get("world_state", {})
    prompt = loader.load_raw("civilization/civilization_system_prompt") + "\n\n" + loader.load_raw(
        "civilization/economy_engine"
    )
    prompt += "\n\nWORLD_STATE:\n" + to_json(world_state)
    prompt += "\n\nRECENT_TOOL_RESULTS:\n" + to_json(state.get("tool_results", []))
    result = invoke_json(prompt, temperature=0.3)
    return {"economy_updates": result}

