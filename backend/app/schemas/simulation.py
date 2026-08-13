from pydantic import BaseModel, Field


class RunSimulationRequest(BaseModel):
    ticks: int = Field(default=1, ge=1, le=500)


class SimulationStatusResponse(BaseModel):
    current_day: int
    current_time: str
    tick_count: int
    status: str
    weather: str
    population: int
    fast_mode: bool = True
    agents_per_tick: int = 3
    simulation_mode: str = "village"
    active_conversations: int
    latest_events: list[dict]
    latest_stories: list[dict]
    last_error: str | None = None
    # Civilization metrics (Phase 4)
    civilization_stage: str = "Village"
    technology_level: float = 0.1
    gdp: float = 0.0
    total_wealth: float = 0.0
    unemployment_rate: float = 0.0
    active_businesses: int = 0
    active_organizations: int = 0
