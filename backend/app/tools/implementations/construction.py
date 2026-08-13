from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.construction_project import ConstructionProject
from app.models.villager import Villager
from app.tools.implementations._helpers import new_id


def start_construction(
    db: Session,
    *,
    villager: Villager,
    tick_id: int | None = None,
    project_type: str,
    total_cost: float,
    duration_days: int = 30,
    location_id: str | None = None,
    **_,
) -> dict:
    cost = float(total_cost)
    if villager.cash < cost * 0.1:
        raise ValueError("Need at least 10% down payment in cash")

    down = cost * 0.1
    villager.cash -= down
    project = ConstructionProject(
        id=new_id("build"),
        owner_type="villager",
        owner_id=villager.id,
        project_type=project_type,
        location_id=location_id,
        total_cost=cost,
        spent=down,
        duration_days=duration_days,
        status="in_progress",
        started_tick=tick_id,
    )
    db.add(project)
    db.flush()
    return {"message": f"Started {project_type}", "project_id": project.id}


def complete_construction(
    db: Session,
    *,
    villager: Villager,
    project_id: str,
    **_,
) -> dict:
    project = (
        db.query(ConstructionProject)
        .filter(
            ConstructionProject.id == project_id,
            ConstructionProject.owner_id == villager.id,
            ConstructionProject.status == "in_progress",
        )
        .first()
    )
    if not project:
        raise ValueError("Project not found")
    remaining = max(0, project.total_cost - project.spent)
    if villager.cash < remaining:
        raise ValueError("Insufficient cash to complete project")
    villager.cash -= remaining
    project.spent = project.total_cost
    project.progress_pct = 100.0
    project.status = "completed"
    db.flush()
    return {"message": f"Completed {project.project_type}", "project_id": project.id}
