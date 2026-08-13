from sqlalchemy.orm import Session

from app.graph.civilization_prompt import (
    fallback_goal_plan,
    normalize_goal_result,
    slim_agent,
    slim_world,
)
from app.graph.civilization_state import CivilizationSimulationState
from app.graph.llm import invoke_json
from app.graph.utils import to_json
from app.prompts.loader import get_prompt_loader
from app.config import get_settings


def civ_goal_planner_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    world_state = state.get("world_state", {})
    agents = state.get("selected_agents", [])
    if not agents:
        return {"goal_plans": []}

    settings = get_settings()
    if settings.simulation_fast_mode:
        return {"goal_plans": [fallback_goal_plan(a) for a in agents]}

    loader = get_prompt_loader()
    slim_ws = slim_world(world_state)
    plans: list[dict] = []
    for a in agents:
        try:
            prompt = loader.load_raw("civilization/civilization_system_prompt") + "\n\n" + loader.load_raw(
                "civilization/goal_planner"
            )
            prompt += "\n\nAGENT:\n" + to_json(slim_agent(a))
            prompt += "\n\nWORLD_STATE:\n" + to_json(slim_ws)
            prompt += (
                "\n\nReturn exactly ONE JSON object with ONLY these keys: "
                'agent_id, short_term_goal, medium_term_goal, long_term_goal, priority. '
                "Numbers must be plain numbers (no math expressions)."
            )

            result = invoke_json(prompt, temperature=0.4)
            plans.append(normalize_goal_result(result, a))
        except Exception:
            plans.append(fallback_goal_plan(a))

    return {"goal_plans": plans}

