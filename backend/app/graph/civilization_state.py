from typing import Any, TypedDict


class CivilizationSimulationState(TypedDict, total=False):
    # Tick metadata
    tick_id: int
    current_day: int
    current_time: str
    weather: str

    # World snapshot (serialized WorldState)
    world_state: dict[str, Any]

    # Selected agents (AgentSnapshot-like dicts)
    selected_agents: list[dict[str, Any]]

    # Goal planning outputs
    goal_plans: list[dict[str, Any]]

    # Decision / tool selection outputs (per agent)
    decisions: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]

    # Engine outputs (LLM-only in Phase 2; DB integration in Phase 3)
    economy_updates: dict[str, Any]
    asset_updates: dict[str, Any]
    business_updates: dict[str, Any]
    construction_updates: dict[str, Any]
    organization_updates: dict[str, Any]
    innovation_updates: dict[str, Any]
    software_updates: dict[str, Any]
    ai_worker_updates: dict[str, Any]
    evolution: dict[str, Any]

    # Side-effect story feed (keep compatibility)
    feed_entries: list[dict[str, Any]]

    error: str | None

