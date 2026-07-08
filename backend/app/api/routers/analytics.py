from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import AccessScope, get_access_scope
from app.db.session import get_db
from app.services.action_engine import SmartInventoryActionEngine
from app.services.analytics_service import AnalyticsService, InsufficientStockError


router = APIRouter(prefix="/analytics", tags=["analytics"])


def waiting_response() -> dict:
    return {
        "requiresStoreAssignment": True,
        "message": "Your Warehouse Owner needs to assign you a store before inventory data is available.",
    }


def service_or_waiting(db: Session, scope: AccessScope) -> AnalyticsService | None:
    return None if scope.requires_store_assignment else AnalyticsService(db, scope)


@router.get("/overview")
def overview(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    service = service_or_waiting(db, scope)
    return waiting_response() if service is None else service.overview()


@router.get("/actions")
def suggested_actions(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    if scope.requires_store_assignment:
        return {"suggestions": [], **waiting_response()}
    return {"suggestions": SmartInventoryActionEngine(db, scope).suggestions()}


@router.get("/inventory")
def inventory(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    service = service_or_waiting(db, scope)
    return {"items": [], **waiting_response()} if service is None else service.inventory()


@router.get("/recommendations")
def recommendations(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    service = service_or_waiting(db, scope)
    return {"recommendations": [], **waiting_response()} if service is None else service.recommendations()


@router.get("/reports")
def reports(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    service = service_or_waiting(db, scope)
    return {"reports": [], **waiting_response()} if service is None else service.reports()


@router.get("/charts")
def charts(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    service = service_or_waiting(db, scope)
    return {"revenueTrend": {"labels": [], "values": []}, "storePerformance": {"labels": [], "values": []}, "categoryMix": {"labels": [], "values": []}, **waiting_response()} if service is None else service.charts()


@router.get("/transfers")
def transfers(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    service = service_or_waiting(db, scope)
    return {"transfers": [], **waiting_response()} if service is None else service.transfers()


@router.get("/inventory-aging")
def inventory_aging(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    service = service_or_waiting(db, scope)
    return {"items": [], **waiting_response()} if service is None else service.inventory_aging()


@router.get("/notices")
def notices(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    service = service_or_waiting(db, scope)
    return {"notices": [], **waiting_response()} if service is None else service.notices()


class InitiateTransferRequest(BaseModel):
    productId: int
    fromStoreId: int
    toStoreId: int
    units: int
    transferCost: float = 0.0


@router.post("/transfers/initiate")
def initiate_transfer(payload: InitiateTransferRequest, scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)):
    if scope.requires_store_assignment:
        raise HTTPException(status_code=403, detail="Store assignment is required")
    service = AnalyticsService(db, scope)
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
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
