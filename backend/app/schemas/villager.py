from pydantic import BaseModel


class VillagerResponse(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    occupation: str
    family_id: str
    location_id: str | None
    current_emotion: str
    emotion_intensity: float

    model_config = {"from_attributes": True}


class MemoryResponse(BaseModel):
    id: int
    content: str
    emotion: str | None
    importance: float
    sim_timestamp: str | None


class RelationshipSummary(BaseModel):
    agent_id: str
    name: str
    friendship: float
    rivalry: float


class VillagerDetailResponse(VillagerResponse):
    education: str | None = None
    personality: list[str] = []
    friends: list[RelationshipSummary] = []
    rivals: list[RelationshipSummary] = []
    memories: list[MemoryResponse] = []
    recent_stories: list[dict] = []
    # Civilization engine fields (dashboards / detail)
    agent_role: str | None = None
    cash: float = 0.0
    bank_balance: float = 0.0
    monthly_income: float = 0.0
    monthly_expenses: float = 0.0
    net_worth: float = 0.0
    reputation: float = 50.0
    skills: list[str] = []
    intelligence: float = 0.5
    employment_status: str = "employed"
