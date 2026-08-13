from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.base import get_db
from app.schemas.civilization import (
    AssetResponse,
    BusinessResponse,
    CivilizationOverviewResponse,
    ConstructionProjectResponse,
    EconomyResponse,
    MetricsResponse,
    OrganizationResponse,
)
from app.services import civilization_queries as cq

router = APIRouter(tags=["civilization"])


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    return MetricsResponse(**cq.get_metrics(db))


@router.get("/economy", response_model=EconomyResponse)
def get_economy(db: Session = Depends(get_db)):
    return EconomyResponse(**cq.get_economy(db))


@router.get("/assets", response_model=list[AssetResponse])
def list_assets(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return [AssetResponse.model_validate(a) for a in cq.list_assets(db, limit=limit)]


@router.get("/businesses", response_model=list[BusinessResponse])
def list_businesses(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    rows = cq.list_businesses(db, limit=limit)
    return [
        BusinessResponse(
            id=r["id"],
            name=r["name"],
            business_type=r["business_type"],
            owner_id=r["owner_id"],
            owner_name=r.get("owner_name"),
            cash=r.get("cash") or 0,
            revenue_monthly=r.get("revenue_monthly") or 0,
            expenses_monthly=r.get("expenses_monthly") or 0,
            employee_count=r.get("employee_count") or 0,
            status=r.get("status") or "active",
        )
        for r in rows
    ]


@router.get("/organizations", response_model=list[OrganizationResponse])
def list_organizations(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    rows = cq.list_organizations(db, limit=limit)
    return [
        OrganizationResponse(
            id=r["id"],
            name=r["name"],
            org_type=r["org_type"],
            owner_id=r.get("owner_id"),
            owner_name=r.get("owner_name"),
            cash=r.get("cash") or 0,
            budget=r.get("budget") or 0,
            reputation=r.get("reputation") or 0,
            technology_level=r.get("technology_level") or 0,
            employee_count=r.get("employee_count") or 0,
            status=r.get("status") or "active",
        )
        for r in rows
    ]


@router.get("/construction", response_model=list[ConstructionProjectResponse])
def list_construction(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return [ConstructionProjectResponse.model_validate(p) for p in cq.list_construction(db, limit=limit)]


@router.get("/civilization", response_model=CivilizationOverviewResponse)
def civilization_overview(db: Session = Depends(get_db)):
    return CivilizationOverviewResponse(**cq.get_civilization_overview(db))
