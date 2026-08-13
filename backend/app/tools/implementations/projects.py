from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.construction_project import ConstructionProject
from app.models.villager import Villager
from app.tools.implementations._helpers import new_id


def create_project(
    db: Session,
    *,
    villager: Villager,
    tick_id: int | None = None,
    project_type: str = "general",
    name: str | None = None,
    **_,
) -> dict:
    project = ConstructionProject(
        id=new_id("proj"),
        owner_type="villager",
        owner_id=villager.id,
        project_type=project_type,
        total_cost=0.0,
        status="planned",
        started_tick=tick_id,
    )
    db.add(project)
    db.flush()
    label = name or project_type
    return {"message": f"Created project {label}", "project_id": project.id}
