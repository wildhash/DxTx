from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Call, CallCreate, CallResponse, CallStatus, CallDirection, OutboundCallRequest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from telephony.telnyx_service import telnyx_service
from agents.state_machine import ConversationStateMachine
from typing import List
import uuid
from datetime import datetime

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/outbound", response_model=CallResponse)
async def initiate_outbound_call(
    request: OutboundCallRequest,
    db: Session = Depends(get_db)
):
    """
    Initiate an outbound call to a patient
    """
    try:
        # Generate unique call ID
        call_id = str(uuid.uuid4())
        
        # Initiate call via Telnyx
        telnyx_result = await telnyx_service.initiate_call(
            to_phone=request.phone_number
        )
        
        # Create call record in database
        call = Call(
            call_id=call_id,
            direction=CallDirection.OUTBOUND,
            status=CallStatus.INITIATED,
            phone_number=request.phone_number,
            patient_name=request.patient_name,
            conversation_state={
                "telnyx_call_control_id": telnyx_result.get("call_control_id"),
                "state_machine": ConversationStateMachine().get_state(),
                "context": request.context or {}
            }
        )
        
        db.add(call)
        db.commit()
        db.refresh(call)
        
        return call
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate call: {str(e)}")


@router.get("/", response_model=List[CallResponse])
async def list_calls(
    skip: int = 0,
    limit: int = 100,
    status: CallStatus = None,
    db: Session = Depends(get_db)
):
    """
    List all calls with optional filtering
    """
    query = db.query(Call)
    
    if status:
        query = query.filter(Call.status == status)
    
    calls = query.order_by(Call.started_at.desc()).offset(skip).limit(limit).all()
    return calls


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(call_id: str, db: Session = Depends(get_db)):
    """
    Get details of a specific call
    """
    call = db.query(Call).filter(Call.call_id == call_id).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return call


@router.post("/{call_id}/hangup")
async def hangup_call(call_id: str, db: Session = Depends(get_db)):
    """
    Hang up an active call
    """
    call = db.query(Call).filter(Call.call_id == call_id).first()
    
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    
    # Get Telnyx call control ID from conversation state
    telnyx_call_control_id = call.conversation_state.get("telnyx_call_control_id")
    
    if not telnyx_call_control_id:
        raise HTTPException(status_code=400, detail="Call control ID not found")
    
    try:
        # Hangup via Telnyx
        await telnyx_service.hangup_call(telnyx_call_control_id)
        
        # Update call status
        call.status = CallStatus.COMPLETED
        call.ended_at = datetime.now()
        
        if call.answered_at:
            call.duration_seconds = int((call.ended_at - call.answered_at).total_seconds())
        
        db.commit()
        
        return {"message": "Call ended successfully", "call_id": call_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to hang up call: {str(e)}")
