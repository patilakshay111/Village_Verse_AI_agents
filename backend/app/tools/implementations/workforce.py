from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.ai_worker import AIWorker
from app.models.organization import Organization
from app.models.villager import Villager
from app.tools.implementations._helpers import new_id


def hire_worker(
    db: Session,
    *,
    villager: Villager,
    tick_id: int | None = None,
    organization_id: str,
    worker_type: str,
    name: str,
    monthly_cost: float = 5000.0,
    **_,
) -> dict:
    org = (
        db.query(Organization)
        .filter(Organization.id == organization_id, Organization.owner_id == villager.id)
        .first()
    )
    if not org:
        raise ValueError("Organization not found or not owned")

    worker = AIWorker(
        id=new_id("aiw"),
        organization_id=org.id,
        worker_type=worker_type,
        name=name,
        monthly_cost=float(monthly_cost),
        responsibilities=json.dumps([]),
        hired_tick=tick_id,
    )
    org.employee_count += 1
    db.add(worker)
    db.flush()
    return {"message": f"Hired {name}", "worker_id": worker.id}


def fire_worker(
    db: Session,
    *,
    villager: Villager,
    worker_id: str,
    **_,
) -> dict:
    worker = (
        db.query(AIWorker)
        .join(Organization, AIWorker.organization_id == Organization.id)
        .filter(AIWorker.id == worker_id, Organization.owner_id == villager.id, AIWorker.status == "active")
        .first()
    )
    if not worker:
        raise ValueError("Worker not found")
    worker.status = "fired"
    org = db.query(Organization).filter(Organization.id == worker.organization_id).first()
    if org and org.employee_count > 0:
        org.employee_count -= 1
    db.flush()
    return {"message": f"Released worker {worker.name}", "worker_id": worker.id}
