from decimal import Decimal
from app.services.decision_impact_service import DecisionImpactEvaluationService
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import AccessScope, get_access_scope
from app.db.session import get_db
from app.services.action_engine import SmartInventoryActionEngine
from app.services.analytics_service import AnalyticsService, InsufficientStockError

router = APIRouter(prefix="/public", tags=["public"])
@router.get("/impact")
def public_impact(db: Session = Depends(get_db)):
    return DecisionImpactEvaluationService(db, scope=None).evaluate()
