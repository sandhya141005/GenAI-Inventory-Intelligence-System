from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import AccessScope, get_access_scope
from app.db.session import get_db
from app.schemas.donations import DonationNotifyRequest
from app.services.donation_service import DonationService


router = APIRouter(prefix="/donations", tags=["donations"])


@router.post("/notify")
def notify_orphanages(
    payload: DonationNotifyRequest,
    scope: AccessScope = Depends(get_access_scope),
    db: Session = Depends(get_db),
) -> dict:
    if scope.requires_store_assignment:
        raise HTTPException(status_code=403, detail="Store assignment is required")
    return DonationService(db, scope).notify_orphanages(payload.product_id)


@router.get("/history")
def donation_history(scope: AccessScope = Depends(get_access_scope), db: Session = Depends(get_db)) -> dict:
    if scope.requires_store_assignment:
        return {
            "items": [],
            "requiresStoreAssignment": True,
            "message": "Your Warehouse Owner needs to assign you a store before donation history is available.",
        }
    return DonationService(db, scope).donation_history()
