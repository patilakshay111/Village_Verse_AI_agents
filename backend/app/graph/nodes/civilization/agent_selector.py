import random

from sqlalchemy.orm import Session

from app.config import get_settings
from app.graph.civilization_state import CivilizationSimulationState
from app.models.location import Location
from app.models.villager import Villager
from app.world.loader import WorldStateLoader


def civ_agent_selector_node(state: CivilizationSimulationState, db: Session) -> CivilizationSimulationState:
    """Select a small set of agents for economic decisioning.

    Phase 2: simple selection; Phase 3 may prioritize based on opportunities, debts, etc.
    """
    settings = get_settings()
    limit = min(3, settings.effective_agents_per_tick or 3)

    villagers = db.query(Villager).all()
    if not villagers:
        return {"selected_agents": []}

    # Prefer villagers with low cash or with businesses (more interesting decisions).
    by_need = sorted(villagers, key=lambda v: (v.cash or 0.0))
    candidates = by_need[: max(limit, 6)]
    random.shuffle(candidates)
    selected = candidates[:limit]

    selected_ids = [v.id for v in selected]
    ws = WorldStateLoader(db).load(tick_id=state.get("tick_id"), selected_agent_ids=selected_ids)
    return {
        "selected_agents": [
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "occupation": a.occupation,
                "agent_role": a.agent_role,
                "cash": a.cash,
                "bank_balance": a.bank_balance,
                "monthly_income": a.monthly_income,
                "monthly_expenses": a.monthly_expenses,
                "net_worth": a.net_worth,
                "reputation": a.reputation,
                "skills": a.skills,
                "goals": a.goals,
                "active_goal_plan": a.active_goal_plan,
                "assets": a.assets,
                "liabilities": a.liabilities,
                "businesses": a.businesses,
                "organizations": a.organizations,
                "permissions": a.permissions,
            }
            for a in ws.selected_agents
        ],
        "world_state": ws.to_dict(),
    }

