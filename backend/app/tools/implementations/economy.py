from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.liability import Liability
from app.models.villager import Villager
from app.tools.implementations._helpers import new_id


def buy_asset(
    db: Session,
    *,
    villager: Villager,
    tick_id: int | None = None,
    asset_type: str,
    name: str,
    price: float,
    monthly_revenue: float = 0.0,
    monthly_cost: float = 0.0,
    location_id: str | None = None,
    **_,
) -> dict:
    price = float(price)
    if villager.cash < price:
        raise ValueError(f"Insufficient cash: have {villager.cash}, need {price}")

    villager.cash -= price
    asset = Asset(
        id=new_id("asset"),
        owner_type="villager",
        owner_id=villager.id,
        asset_type=asset_type,
        name=name,
        value=price,
        monthly_revenue=monthly_revenue,
        monthly_cost=monthly_cost,
        location_id=location_id,
        acquired_tick=tick_id,
    )
    db.add(asset)
    villager.net_worth = (villager.net_worth or 0) + price
    db.flush()
    return {"message": f"Bought {name}", "asset_id": asset.id, "cash_remaining": villager.cash}


def sell_asset(
    db: Session,
    *,
    villager: Villager,
    asset_id: str,
    sale_price: float | None = None,
    **_,
) -> dict:
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.owner_id == villager.id).first()
    if not asset:
        raise ValueError("Asset not found or not owned")
    price = float(sale_price if sale_price is not None else asset.value)
    villager.cash += price
    villager.net_worth = max(0, (villager.net_worth or 0) - asset.value)
    asset.status = "sold"
    db.flush()
    return {"message": f"Sold {asset.name}", "asset_id": asset.id, "proceeds": price}


def take_loan(
    db: Session,
    *,
    villager: Villager,
    tick_id: int | None = None,
    amount: float,
    interest_rate: float = 0.12,
    term_months: int = 12,
    **_,
) -> dict:
    amount = float(amount)
    monthly = amount * (1 + interest_rate) / max(term_months, 1)
    liability = Liability(
        id=new_id("loan"),
        owner_type="villager",
        owner_id=villager.id,
        liability_type="personal_loan",
        principal=amount,
        balance=amount * (1 + interest_rate),
        interest_rate=interest_rate,
        monthly_payment=monthly,
        opened_tick=tick_id,
    )
    villager.cash += amount
    db.add(liability)
    db.flush()
    return {"message": f"Loan of {amount} approved", "liability_id": liability.id}


def repay_loan(
    db: Session,
    *,
    villager: Villager,
    liability_id: str,
    amount: float | None = None,
    **_,
) -> dict:
    liability = (
        db.query(Liability)
        .filter(Liability.id == liability_id, Liability.owner_id == villager.id, Liability.status == "active")
        .first()
    )
    if not liability:
        raise ValueError("Loan not found")
    pay = float(amount if amount is not None else min(liability.balance, villager.cash))
    if villager.cash < pay:
        raise ValueError("Insufficient cash to repay")
    villager.cash -= pay
    liability.balance = max(0, liability.balance - pay)
    if liability.balance <= 0:
        liability.status = "closed"
    db.flush()
    return {"message": "Loan repayment recorded", "remaining_balance": liability.balance}
