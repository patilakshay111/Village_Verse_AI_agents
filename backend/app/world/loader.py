"""Load WorldState from the database."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.agents.roles import permissions_for_role
from app.config import get_settings
from app.models.asset import Asset
from app.models.business import Business
from app.models.construction_project import ConstructionProject
from app.models.liability import Liability
from app.models.market_price import MarketPrice
from app.models.organization import Organization
from app.models.simulation_run import SimulationRun
from app.models.villager import Villager
from app.world.state import AgentSnapshot, EconomySnapshot, WorldState


def _parse_json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


class WorldStateLoader:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _sim(self) -> SimulationRun:
        sim = self.db.query(SimulationRun).order_by(SimulationRun.id.desc()).first()
        if not sim:
            sim = SimulationRun()
            self.db.add(sim)
            self.db.flush()
        return sim

    def load(
        self,
        *,
        tick_id: int | None = None,
        selected_agent_ids: list[str] | None = None,
    ) -> WorldState:
        settings = get_settings()
        sim = self._sim()
        villagers = self.db.query(Villager).all()
        tick = tick_id if tick_id is not None else (sim.tick_count or 0) + 1

        assets = self.db.query(Asset).filter(Asset.status == "active").all()
        businesses = self.db.query(Business).filter(Business.status == "active").all()
        organizations = self.db.query(Organization).filter(Organization.status == "active").all()
        projects = self.db.query(ConstructionProject).filter(
            ConstructionProject.status.in_(("planned", "in_progress"))
        ).all()
        prices = self.db.query(MarketPrice).order_by(MarketPrice.id.desc()).limit(50).all()

        total_wealth = sum(v.cash + v.bank_balance + v.net_worth for v in villagers)
        unemployed = sum(1 for v in villagers if v.employment_status == "unemployed")
        population = len(villagers) or 1

        economy = EconomySnapshot(
            gdp=sim.gdp or 0.0,
            total_wealth=sim.total_wealth or total_wealth,
            unemployment_rate=sim.unemployment_rate or (unemployed / population),
            active_businesses=len(businesses),
            active_organizations=len(organizations),
        )

        agent_ids = selected_agent_ids or []
        selected_villagers = (
            [v for v in villagers if v.id in agent_ids]
            if agent_ids
            else []
        )

        snapshots = [self._agent_snapshot(v, assets, businesses, organizations) for v in selected_villagers]

        return WorldState(
            tick_id=tick,
            current_day=sim.current_day or 1,
            current_time=sim.current_time or "Morning",
            weather=sim.weather or "Clear",
            village_name=settings.village_name,
            population=population,
            civilization_stage=sim.civilization_stage or "Village",
            technology_level=sim.technology_level or 0.1,
            economy=economy,
            market_prices=[self._market_price_row(p) for p in prices],
            businesses=[self._business_row(b) for b in businesses],
            organizations=[self._organization_row(o) for o in organizations],
            assets=[self._asset_row(a) for a in assets],
            active_projects=[self._project_row(p) for p in projects],
            selected_agents=snapshots,
        )

    def _agent_snapshot(
        self,
        v: Villager,
        all_assets: list[Asset],
        all_businesses: list[Business],
        all_orgs: list[Organization],
    ) -> AgentSnapshot:
        my_assets = [a for a in all_assets if a.owner_type == "villager" and a.owner_id == v.id]
        liabilities = (
            self.db.query(Liability)
            .filter(Liability.owner_type == "villager", Liability.owner_id == v.id, Liability.status == "active")
            .all()
        )
        my_businesses = [b for b in all_businesses if b.owner_id == v.id]
        my_orgs = [o for o in all_orgs if o.owner_id == v.id]

        role = v.agent_role or "villager"
        return AgentSnapshot(
            agent_id=v.id,
            name=v.name,
            age=v.age,
            occupation=v.occupation,
            agent_role=role,
            family_id=v.family_id,
            location_id=v.location_id,
            cash=v.cash or 0.0,
            bank_balance=v.bank_balance or 0.0,
            monthly_income=v.monthly_income or 0.0,
            monthly_expenses=v.monthly_expenses or 0.0,
            net_worth=v.net_worth or 0.0,
            reputation=v.reputation or 50.0,
            skills=_parse_json(v.skills, []),
            goals=_parse_json(v.goals, {}),
            active_goal_plan=_parse_json(v.active_goal_plan, {}),
            assets=[self._asset_row(a) for a in my_assets],
            liabilities=[self._liability_row(l) for l in liabilities],
            businesses=[self._business_row(b) for b in my_businesses],
            organizations=[self._organization_row(o) for o in my_orgs],
            permissions=sorted(permissions_for_role(role)),
        )

    @staticmethod
    def _asset_row(a: Asset) -> dict[str, Any]:
        return {
            "id": a.id,
            "owner_type": a.owner_type,
            "owner_id": a.owner_id,
            "asset_type": a.asset_type,
            "name": a.name,
            "value": a.value,
            "monthly_revenue": a.monthly_revenue,
            "monthly_cost": a.monthly_cost,
            "status": a.status,
        }

    @staticmethod
    def _liability_row(l: Liability) -> dict[str, Any]:
        return {
            "id": l.id,
            "liability_type": l.liability_type,
            "balance": l.balance,
            "monthly_payment": l.monthly_payment,
            "status": l.status,
        }

    @staticmethod
    def _business_row(b: Business) -> dict[str, Any]:
        return {
            "id": b.id,
            "name": b.name,
            "business_type": b.business_type,
            "owner_id": b.owner_id,
            "cash": b.cash,
            "revenue_monthly": b.revenue_monthly,
            "expenses_monthly": b.expenses_monthly,
            "employee_count": b.employee_count,
            "status": b.status,
        }

    @staticmethod
    def _organization_row(o: Organization) -> dict[str, Any]:
        return {
            "id": o.id,
            "name": o.name,
            "org_type": o.org_type,
            "owner_id": o.owner_id,
            "cash": o.cash,
            "budget": o.budget,
            "reputation": o.reputation,
            "technology_level": o.technology_level,
            "employee_count": o.employee_count,
            "status": o.status,
        }

    @staticmethod
    def _project_row(p: ConstructionProject) -> dict[str, Any]:
        return {
            "id": p.id,
            "owner_type": p.owner_type,
            "owner_id": p.owner_id,
            "project_type": p.project_type,
            "total_cost": p.total_cost,
            "spent": p.spent,
            "progress_pct": p.progress_pct,
            "status": p.status,
        }

    @staticmethod
    def _market_price_row(p: MarketPrice) -> dict[str, Any]:
        return {
            "market_id": p.market_id,
            "commodity": p.commodity,
            "price": p.price,
            "supply": p.supply,
            "demand": p.demand,
            "tick_id": p.tick_id,
        }
