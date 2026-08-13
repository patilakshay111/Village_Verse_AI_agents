from typing import Any, TypedDict


class SimulationState(TypedDict, total=False):
    tick_id: int
    current_day: int
    current_time: str
    weather: str
    world_state: dict[str, Any]
    events: list[dict[str, Any]]
    selected_agents: list[dict[str, Any]]
    location: dict[str, Any]
    relationships: list[dict[str, Any]]
    memories: list[dict[str, Any]]
    conversation: list[dict[str, Any]]
    important_moments: list[str]
    new_memories: list[dict[str, Any]]
    relationship_updates: list[dict[str, Any]]
    emotion_updates: list[dict[str, Any]]
    rumors: list[dict[str, Any]]
    updated_rumors: list[dict[str, Any]]
    feed_entries: list[dict[str, Any]]
    error: str | None
