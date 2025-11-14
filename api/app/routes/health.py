from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Call, CallStatus, CallSummary
from sqlalchemy import func

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "DxTx API",
        "version": "1.0.0"
    }


@router.get("/stats", response_model=CallSummary)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get call statistics
    """
    total_calls = db.query(Call).count()
    active_calls = db.query(Call).filter(
        Call.status.in_([CallStatus.INITIATED, CallStatus.RINGING, CallStatus.ANSWERED, CallStatus.IN_PROGRESS])
    ).count()
    completed_calls = db.query(Call).filter(Call.status == CallStatus.COMPLETED).count()
    failed_calls = db.query(Call).filter(Call.status == CallStatus.FAILED).count()
    
    return CallSummary(
        total_calls=total_calls,
        active_calls=active_calls,
        completed_calls=completed_calls,
        failed_calls=failed_calls
    )
