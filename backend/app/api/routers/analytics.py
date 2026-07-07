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
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics_service import AnalyticsService, InsufficientStockError


class InitiateTransferRequest(BaseModel):
    productId: int
    fromStoreId: int
    toStoreId: int
    units: int
    transferCost: float = 0.0


@router.post("/transfers/initiate")
def initiate_transfer(payload: InitiateTransferRequest, db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    try:
        return service.initiate_transfer(
            product_id=payload.productId,
            from_store_id=payload.fromStoreId,
            to_store_id=payload.toStoreId,
            quantity=payload.units,
            transfer_cost=Decimal(str(payload.transferCost)),
        )
    except InsufficientStockError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))