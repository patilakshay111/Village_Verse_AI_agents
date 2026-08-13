from sqlalchemy.orm import Session

from app.graph.civilization_prompt import (
    fallback_decision,
    normalize_decision_result,
    slim_agent,
    slim_world,
)
from app.graph.civilization_state import CivilizationSimulationState
from app.graph.llm import invoke_json
from app.graph.utils import to_json
from app.prompts.loader import get_prompt_loader
from app.tools.registry import get_tool_registry
from app.config import get_settings


def civ_decision_engine_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    registry = get_tool_registry()
    world_state = state.get("world_state", {})
    agents = state.get("selected_agents", [])
    plans = {p.get("agent_id"): p for p in state.get("goal_plans", []) if isinstance(p, dict)}

    settings = get_settings()
    if settings.simulation_fast_mode:
        decisions = []
        for a in agents:
            role = a.get("agent_role", "villager")
            available_tools = registry.list_tools_for_role(role)
            decisions.append(fallback_decision(a, available_tools))
        return {"decisions": decisions}

    loader = get_prompt_loader()
    slim_ws = slim_world(world_state)
    decisions: list[dict] = []
    for a in agents:
        agent_id = a.get("agent_id")
        role = a.get("agent_role", "villager")
        available_tools = registry.list_tools_for_role(role)
        tool_summaries = [
            {"name": t.get("name"), "description": (t.get("description") or "")[:80]}
            for t in available_tools
        ]

        prompt = loader.load_raw("civilization/civilization_system_prompt") + "\n\n" + loader.render(
            "civilization/decision_engine",
            available_tools=to_json(tool_summaries),
            assets=to_json({"count": len(a.get("assets") or []), "sample": (a.get("assets") or [])[:2]}),
            goals=to_json(plans.get(agent_id) or a.get("active_goal_plan") or {}),
            liabilities=to_json({"count": len(a.get("liabilities") or []), "sample": (a.get("liabilities") or [])[:2]}),
            relationships=to_json([]),
        )
        prompt += "\n\nAGENT:\n" + to_json(slim_agent(a))
        prompt += "\n\nWORLD_STATE:\n" + to_json(slim_ws)
        prompt += (
            "\n\nReturn ONE JSON object with ONLY: selected_tool, reason, expected_benefit. "
            "expected_benefit must be a plain string (not an object). "
            "Use plain numbers only — no math like 100+50."
        )

        try:
            result = invoke_json(prompt, temperature=0.35)
            decisions.append(normalize_decision_result(result, a))
        except Exception:
            decisions.append(fallback_decision(a, available_tools))

    return {"decisions": decisions}

