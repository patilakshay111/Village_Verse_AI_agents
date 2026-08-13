"""Seed civilization data: markets, financial backfill, agent roles."""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.agents.roles import infer_role_from_occupation
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.villager import Villager

DEFAULT_MARKETS = [
    ("village_market", "Village Market", "General goods and produce"),
    ("labor_market", "Labor Market", "Daily wages and skilled labor"),
    ("construction_market", "Construction Market", "Cement, steel, materials"),
]

DEFAULT_COMMODITIES = [
    ("village_market", "wheat", 2200.0),
    ("village_market", "milk", 55.0),
    ("village_market", "fuel", 95.0),
    ("labor_market", "farm_labor", 350.0),
    ("labor_market", "skilled_labor", 800.0),
    ("construction_market", "cement", 420.0),
    ("construction_market", "software_license", 15000.0),
]

_WEALTH_BAND_CASH = {
    "Poor": (2000, 8000),
    "Middle": (15000, 45000),
    "Comfortable": (50000, 150000),
}


def seed_markets(db: Session, tick_id: int = 0) -> None:
    for mid, name, desc in DEFAULT_MARKETS:
        if db.query(Market).filter(Market.id == mid).first():
            continue
        db.add(Market(id=mid, name=name, description=desc))

    db.flush()

    for market_id, commodity, price in DEFAULT_COMMODITIES:
        exists = (
            db.query(MarketPrice)
            .filter(MarketPrice.market_id == market_id, MarketPrice.commodity == commodity)
            .first()
        )
        if exists:
            continue
        db.add(
            MarketPrice(
                market_id=market_id,
                commodity=commodity,
                price=price,
                supply=100.0,
                demand=100.0,
                tick_id=tick_id,
            )
        )
    db.flush()


def backfill_villager_finances(db: Session) -> int:
    """Assign roles, cash, and skills from existing seed data. Idempotent-ish."""
    import random

    updated = 0
    for v in db.query(Villager).all():
        role = infer_role_from_occupation(v.occupation)
        v.agent_role = role.value

        if (v.cash or 0) <= 0:
            band = v.financial_status or "Middle"
            lo, hi = _WEALTH_BAND_CASH.get(band, (10000, 30000))
            v.cash = float(random.randint(lo, hi))
            v.bank_balance = float(random.randint(0, int(v.cash * 0.5)))
            v.monthly_income = float(random.randint(8000, 35000))
            v.monthly_expenses = float(random.randint(5000, int(v.monthly_income * 0.8)))
            v.net_worth = v.cash + v.bank_balance
            v.reputation = v.reputation or 50.0

        if not v.skills:
            skill_map = {
                "Farmer": ["farming", "negotiation"],
                "Shopkeeper": ["sales", "inventory"],
                "Teacher": ["teaching", "writing"],
                "Contractor": ["construction", "management"],
                "Sarpanch": ["politics", "negotiation"],
                "Gram Sevak": ["administration", "records"],
            }
            v.skills = json.dumps(skill_map.get(v.occupation, ["general_labor"]))

        if v.employment_status is None or v.employment_status == "":
            v.employment_status = "employed"

        updated += 1

    db.flush()
    return updated


def seed_civilization_basics(db: Session) -> dict:
    markets_before = db.query(Market).count()
    seed_markets(db)
    villagers = backfill_villager_finances(db)
    return {
        "markets": db.query(Market).count() - markets_before,
        "villagers_backfilled": villagers,
    }
