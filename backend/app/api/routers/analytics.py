from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.action_engine import SmartInventoryActionEngine
from app.services.analytics_service import AnalyticsService


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)) -> dict:
    return AnalyticsService(db).overview()


@router.get("/actions")
def suggested_actions(db: Session = Depends(get_db)) -> dict:
    return {"suggestions": SmartInventoryActionEngine(db).suggestions()}


@router.get("/inventory")
def inventory(db: Session = Depends(get_db)) -> dict:
    return AnalyticsService(db).inventory()


@router.get("/recommendations")
def recommendations(db: Session = Depends(get_db)) -> dict:
    return AnalyticsService(db).recommendations()


@router.get("/reports")
def reports(db: Session = Depends(get_db)) -> dict:
    return AnalyticsService(db).reports()


@router.get("/charts")
def charts(db: Session = Depends(get_db)) -> dict:
    return AnalyticsService(db).charts()


@router.get("/transfers")
def transfers(db: Session = Depends(get_db)) -> dict:
    return AnalyticsService(db).transfers()


@router.get("/inventory-aging")
def inventory_aging(db: Session = Depends(get_db)) -> dict:
    return AnalyticsService(db).inventory_aging()


@router.get("/notices")
def notices(db: Session = Depends(get_db)) -> dict:
    return AnalyticsService(db).notices()
