from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.donations import DonationNotifyRequest
from app.services.donation_service import DonationService


router = APIRouter(prefix="/donations", tags=["donations"])


@router.post("/notify")
def notify_orphanages(payload: DonationNotifyRequest, db: Session = Depends(get_db)) -> dict:
    return DonationService(db).notify_orphanages(payload.product_id)


@router.get("/history")
def donation_history(db: Session = Depends(get_db)) -> dict:
    return DonationService(db).donation_history()
