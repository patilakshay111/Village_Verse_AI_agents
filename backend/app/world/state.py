"""Typed world state snapshot for civilization simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EconomySnapshot:
    gdp: float = 0.0
    total_wealth: float = 0.0
    unemployment_rate: float = 0.0
    inflation_rate: float = 0.02
    active_businesses: int = 0
    active_organizations: int = 0


@dataclass
class AgentSnapshot:
    agent_id: str
    name: str
    age: int
    occupation: str
    agent_role: str
    family_id: str
    location_id: str | None
    cash: float
    bank_balance: float
    monthly_income: float
    monthly_expenses: float
    net_worth: float
    reputation: float
    skills: list[str]
    goals: dict[str, Any]
    active_goal_plan: dict[str, Any]
    assets: list[dict[str, Any]] = field(default_factory=list)
    liabilities: list[dict[str, Any]] = field(default_factory=list)
    businesses: list[dict[str, Any]] = field(default_factory=list)
    organizations: list[dict[str, Any]] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)


@dataclass
class WorldState:
    tick_id: int
    current_day: int
    current_time: str
    weather: str
    village_name: str
    population: int
    civilization_stage: str
    technology_level: float
    economy: EconomySnapshot
    market_prices: list[dict[str, Any]]
    businesses: list[dict[str, Any]]
    organizations: list[dict[str, Any]]
    assets: list[dict[str, Any]]
    active_projects: list[dict[str, Any]]
    selected_agents: list[AgentSnapshot] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return world_state_to_dict(self)


def world_state_to_dict(state: WorldState) -> dict[str, Any]:
    return {
        "tick_id": state.tick_id,
        "current_day": state.current_day,
        "current_time": state.current_time,
        "weather": state.weather,
        "village_name": state.village_name,
        "population": state.population,
        "civilization_stage": state.civilization_stage,
        "technology_level": state.technology_level,
        "economy": {
            "gdp": state.economy.gdp,
            "total_wealth": state.economy.total_wealth,
            "unemployment_rate": state.economy.unemployment_rate,
            "inflation_rate": state.economy.inflation_rate,
            "active_businesses": state.economy.active_businesses,
            "active_organizations": state.economy.active_organizations,
        },
        "market_prices": state.market_prices,
        "businesses": state.businesses,
        "organizations": state.organizations,
        "assets": state.assets,
        "active_projects": state.active_projects,
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
            for a in state.selected_agents
        ],
    }
