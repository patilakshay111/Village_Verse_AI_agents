"""Compact LLM context for civilization nodes (small models choke on huge JSON)."""

from __future__ import annotations

from typing import Any


def slim_agent(agent: dict[str, Any]) -> dict[str, Any]:
    """Minimal agent context for goal/decision prompts."""
    assets = agent.get("assets") or []
    liabilities = agent.get("liabilities") or []
    businesses = agent.get("businesses") or []
    organizations = agent.get("organizations") or []
    skills = agent.get("skills") or []
    if isinstance(skills, str):
        skills = [skills]

    return {
        "agent_id": agent.get("agent_id"),
        "name": agent.get("name"),
        "occupation": agent.get("occupation"),
        "agent_role": agent.get("agent_role"),
        "cash": agent.get("cash"),
        "bank_balance": agent.get("bank_balance"),
        "monthly_income": agent.get("monthly_income"),
        "monthly_expenses": agent.get("monthly_expenses"),
        "net_worth": agent.get("net_worth"),
        "reputation": agent.get("reputation"),
        "skills": skills[:5],
        "asset_count": len(assets),
        "liability_count": len(liabilities),
        "business_count": len(businesses),
        "organization_count": len(organizations),
    }


def slim_world(world_state: dict[str, Any]) -> dict[str, Any]:
    """Macro snapshot only — avoid dumping every asset/business row."""
    economy = world_state.get("economy") or {}
    prices = world_state.get("market_prices") or []
    return {
        "tick_id": world_state.get("tick_id"),
        "current_day": world_state.get("current_day"),
        "current_time": world_state.get("current_time"),
        "civilization_stage": world_state.get("civilization_stage"),
        "technology_level": world_state.get("technology_level"),
        "economy": {
            "gdp": economy.get("gdp"),
            "total_wealth": economy.get("total_wealth"),
            "unemployment_rate": economy.get("unemployment_rate"),
            "active_businesses": economy.get("active_businesses"),
            "active_organizations": economy.get("active_organizations"),
        },
        "market_prices": prices[:6],
        "active_project_count": len(world_state.get("active_projects") or []),
    }


def fallback_goal_plan(agent: dict[str, Any]) -> dict[str, Any]:
    occ = agent.get("occupation") or "Villager"
    role = agent.get("agent_role") or "villager"
    if role == "farmer":
        short, medium, long = "Buy seeds for next season", "Acquire a tractor", "Become the largest farm"
    elif role == "shopkeeper":
        short, medium, long = "Restock inventory", "Expand shop", "Open a second branch"
    elif role == "teacher":
        short, medium, long = "Improve school resources", "Start tuition classes", "Build an education company"
    else:
        short = f"Improve daily earnings as {occ}"
        medium = "Invest in an income asset"
        long = "Grow influence through stable wealth"
    return {
        "agent_id": agent.get("agent_id"),
        "short_term_goal": short,
        "medium_term_goal": medium,
        "long_term_goal": long,
        "priority": 0.5,
    }


def fallback_decision(agent: dict[str, Any], available_tools: list[dict[str, Any]]) -> dict[str, Any]:
    role = agent.get("agent_role") or "villager"
    cash = float(agent.get("cash") or 0)
    preferred_by_role: dict[str, list[str]] = {
        "farmer": ["buy_asset", "take_loan", "create_business"],
        "shopkeeper": ["create_business", "buy_asset", "take_loan"],
        "teacher": ["create_business", "buy_asset", "start_construction"],
        "contractor": ["start_construction", "buy_asset", "create_business"],
        "sarpanch": ["start_construction", "create_business", "hire_worker"],
    }
    tool_names = [t.get("name") for t in available_tools if t.get("name")]
    preferred = preferred_by_role.get(role, ["create_business", "buy_asset", "take_loan", "start_construction"])
    selected = next((t for t in preferred if t in tool_names), None)
    if not selected and tool_names:
        selected = tool_names[0]
    if not selected:
        selected = "buy_asset"
    if selected == "buy_asset" and cash < 500:
        selected = next((t for t in ("take_loan", "create_business") if t in tool_names), selected)
    return {
        "selected_tool": selected,
        "reason": f"Heuristic choice for {role}",
        "expected_benefit": "Steady income and village growth",
        "agent_id": agent.get("agent_id"),
    }


def normalize_goal_result(result: dict[str, Any], agent: dict[str, Any]) -> dict[str, Any]:
    """Accept partial/echoed LLM output and coerce to goal schema."""
    if result.get("short_term_goal"):
        return {
            "agent_id": result.get("agent_id") or agent.get("agent_id"),
            "short_term_goal": str(result.get("short_term_goal", ""))[:200],
            "medium_term_goal": str(result.get("medium_term_goal", ""))[:200],
            "long_term_goal": str(result.get("long_term_goal", ""))[:200],
            "priority": float(result.get("priority", 0.5) or 0.5),
        }
    return fallback_goal_plan(agent)


def normalize_decision_result(result: dict[str, Any], agent: dict[str, Any]) -> dict[str, Any]:
    """Coerce decision output; models often put math/objects in expected_benefit."""
    benefit = result.get("expected_benefit", "")
    if isinstance(benefit, dict):
        benefit = ", ".join(f"{k}={v}" for k, v in benefit.items())
    elif benefit is None:
        benefit = ""
    else:
        benefit = str(benefit)[:300]

    tool = result.get("selected_tool") or result.get("tool") or ""
    tool = str(tool).strip()
    return {
        "agent_id": result.get("agent_id") or agent.get("agent_id"),
        "selected_tool": tool or fallback_decision(agent, []).get("selected_tool"),
        "reason": str(result.get("reason", "LLM decision"))[:300],
        "expected_benefit": benefit or "Economic improvement",
    }
