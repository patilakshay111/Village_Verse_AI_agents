from pydantic import BaseModel


class AssetResponse(BaseModel):
    id: str
    owner_type: str
    owner_id: str
    asset_type: str
    name: str
    value: float
    monthly_revenue: float
    monthly_cost: float
    status: str
    location_id: str | None = None

    model_config = {"from_attributes": True}


class BusinessResponse(BaseModel):
    id: str
    name: str
    business_type: str
    owner_id: str
    owner_name: str | None = None
    cash: float
    revenue_monthly: float
    expenses_monthly: float
    employee_count: int
    status: str

    model_config = {"from_attributes": True}


class OrganizationResponse(BaseModel):
    id: str
    name: str
    org_type: str
    owner_id: str | None
    owner_name: str | None = None
    cash: float
    budget: float
    reputation: float
    technology_level: float
    employee_count: int
    status: str

    model_config = {"from_attributes": True}


class ConstructionProjectResponse(BaseModel):
    id: str
    owner_type: str
    owner_id: str
    project_type: str
    total_cost: float
    spent: float
    progress_pct: float
    status: str
    location_id: str | None = None

    model_config = {"from_attributes": True}


class MarketPriceResponse(BaseModel):
    market_id: str
    commodity: str
    price: float
    supply: float
    demand: float


class EconomyResponse(BaseModel):
    gdp: float
    total_wealth: float
    unemployment_rate: float
    inflation_rate: float
    active_businesses: int
    active_organizations: int
    market_prices: list[MarketPriceResponse]


class CivilizationOverviewResponse(BaseModel):
    civilization_stage: str
    technology_level: float
    next_stage: str | None = None
    requirements: list[str] = []


class TopFamilyItem(BaseModel):
    family_id: str
    name: str
    wealth: float
    reputation: float
    member_count: int


class TopBusinessItem(BaseModel):
    business_id: str
    name: str
    business_type: str
    revenue_monthly: float
    owner_name: str | None = None


class MetricsResponse(BaseModel):
    total_wealth: float
    gdp: float
    active_businesses: int
    active_organizations: int
    population: int
    unemployment_rate: float
    technology_level: float
    civilization_stage: str
    simulation_mode: str
    top_families: list[TopFamilyItem]
    top_businesses: list[TopBusinessItem]
