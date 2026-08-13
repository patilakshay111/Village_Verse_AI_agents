"""Read-only queries for civilization dashboards and metrics."""

from __future__ import annotations

import json

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.asset import Asset
from app.models.business import Business
from app.models.construction_project import ConstructionProject
from app.models.family import Family
from app.models.market_price import MarketPrice
from app.models.organization import Organization
from app.models.simulation_run import SimulationRun
from app.models.villager import Villager
from app.world.loader import WorldStateLoader


def _sim(db: Session) -> SimulationRun:
    return db.query(SimulationRun).order_by(SimulationRun.id.desc()).first() or SimulationRun()


def get_metrics(db: Session) -> dict:
    settings = get_settings()
    sim = _sim(db)
    ws = WorldStateLoader(db).load()

    families = db.query(Family).all()
    family_wealth: list[dict] = []
    for f in families:
        members = db.query(Villager).filter(Villager.family_id == f.id).all()
        wealth = sum((m.cash or 0) + (m.bank_balance or 0) + (m.net_worth or 0) for m in members)
        family_wealth.append(
            {
                "family_id": f.id,
                "name": f.name,
                "wealth": wealth + (f.wealth or 0),
                "reputation": f.reputation or 0,
                "member_count": len(members),
            }
        )
    family_wealth.sort(key=lambda x: x["wealth"], reverse=True)

    businesses = (
        db.query(Business)
        .filter(Business.status == "active")
        .order_by(Business.revenue_monthly.desc())
        .limit(5)
        .all()
    )
    top_biz = []
    for b in businesses:
        owner = db.query(Villager).filter(Villager.id == b.owner_id).first()
        top_biz.append(
            {
                "business_id": b.id,
                "name": b.name,
                "business_type": b.business_type,
                "revenue_monthly": b.revenue_monthly or 0,
                "owner_name": owner.name if owner else None,
            }
        )

    unemployed = db.query(Villager).filter(Villager.employment_status == "unemployed").count()
    population = db.query(Villager).count() or 1

    return {
        "total_wealth": sim.total_wealth or ws.economy.total_wealth,
        "gdp": sim.gdp or ws.economy.gdp,
        "active_businesses": ws.economy.active_businesses,
        "active_organizations": ws.economy.active_organizations,
        "population": population,
        "unemployment_rate": sim.unemployment_rate or (unemployed / population),
        "technology_level": sim.technology_level or ws.technology_level,
        "civilization_stage": sim.civilization_stage or ws.civilization_stage,
        "simulation_mode": settings.simulation_mode,
        "top_families": family_wealth[:5],
        "top_businesses": top_biz,
    }


def get_economy(db: Session) -> dict:
    sim = _sim(db)
    ws = WorldStateLoader(db).load()
    inflation = 0.02
    if sim.economy_snapshot:
        try:
            snap = json.loads(sim.economy_snapshot)
            inflation = float(snap.get("inflation_rate", inflation))
        except json.JSONDecodeError:
            pass

    prices = (
        db.query(MarketPrice)
        .order_by(MarketPrice.id.desc())
        .limit(20)
        .all()
    )
    # Deduplicate by commodity (latest first)
    seen: set[tuple[str, str]] = set()
    market_prices: list[dict] = []
    for p in prices:
        key = (p.market_id, p.commodity)
        if key in seen:
            continue
        seen.add(key)
        market_prices.append(
            {
                "market_id": p.market_id,
                "commodity": p.commodity,
                "price": p.price,
                "supply": p.supply,
                "demand": p.demand,
            }
        )

    return {
        "gdp": sim.gdp or ws.economy.gdp,
        "total_wealth": sim.total_wealth or ws.economy.total_wealth,
        "unemployment_rate": sim.unemployment_rate or ws.economy.unemployment_rate,
        "inflation_rate": inflation,
        "active_businesses": ws.economy.active_businesses,
        "active_organizations": ws.economy.active_organizations,
        "market_prices": market_prices,
    }


def list_assets(db: Session, *, limit: int = 50) -> list[Asset]:
    return (
        db.query(Asset)
        .filter(Asset.status == "active")
        .order_by(Asset.value.desc())
        .limit(limit)
        .all()
    )


def list_businesses(db: Session, *, limit: int = 50) -> list[dict]:
    rows = (
        db.query(Business)
        .filter(Business.status == "active")
        .order_by(Business.revenue_monthly.desc())
        .limit(limit)
        .all()
    )
    out = []
    for b in rows:
        owner = db.query(Villager).filter(Villager.id == b.owner_id).first()
        out.append({**b.__dict__, "owner_name": owner.name if owner else None})
    return out


def list_organizations(db: Session, *, limit: int = 50) -> list[dict]:
    rows = (
        db.query(Organization)
        .filter(Organization.status == "active")
        .order_by(Organization.reputation.desc())
        .limit(limit)
        .all()
    )
    out = []
    for o in rows:
        owner = db.query(Villager).filter(Villager.id == o.owner_id).first() if o.owner_id else None
        out.append({**o.__dict__, "owner_name": owner.name if owner else None})
    return out


def list_construction(db: Session, *, limit: int = 50) -> list[ConstructionProject]:
    return (
        db.query(ConstructionProject)
        .filter(ConstructionProject.status.in_(("planned", "in_progress")))
        .order_by(ConstructionProject.progress_pct.desc())
        .limit(limit)
        .all()
    )


def get_civilization_overview(db: Session) -> dict:
    sim = _sim(db)
    ws = WorldStateLoader(db).load()
    stage = sim.civilization_stage or ws.civilization_stage or "Village"
    next_stage = "Town"
    requirements: list[str] = []
    if stage == "Village":
        next_stage = "Town"
        requirements = ["5+ active businesses OR 3+ organizations", "Growing total wealth"]
    elif stage == "Town":
        next_stage = "City"
        requirements = ["10+ businesses", "Higher technology level"]
    else:
        next_stage = None
        requirements = ["Continue expanding economy and infrastructure"]

    return {
        "civilization_stage": stage,
        "technology_level": sim.technology_level or ws.technology_level,
        "next_stage": next_stage,
        "requirements": requirements,
    }
