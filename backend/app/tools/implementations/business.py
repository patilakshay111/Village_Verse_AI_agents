from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.villager import Villager
from app.tools.implementations._helpers import new_id


def create_business(
    db: Session,
    *,
    villager: Villager,
    tick_id: int | None = None,
    name: str,
    business_type: str,
    startup_cost: float = 0.0,
    **_,
) -> dict:
    cost = float(startup_cost)
    if villager.cash < cost:
        raise ValueError(f"Need {cost} cash to start {name}")

    villager.cash -= cost
    villager.agent_role = "business_owner"
    villager.employment_status = "owner"
    biz = Business(
        id=new_id("biz"),
        name=name,
        business_type=business_type,
        owner_id=villager.id,
        cash=cost * 0.2,
        founded_tick=tick_id,
        metadata_json=json.dumps({"startup_cost": cost}),
    )
    db.add(biz)
    db.flush()
    return {"message": f"Created business {name}", "business_id": biz.id}
