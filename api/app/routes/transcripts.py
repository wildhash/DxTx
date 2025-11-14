from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transcript, TranscriptEntry, TranscriptResponse
from typing import List

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.get("/{call_id}", response_model=TranscriptResponse)
async def get_call_transcript(call_id: str, db: Session = Depends(get_db)):
    """
    Get the full transcript for a call
    """
    transcripts = db.query(Transcript).filter(
        Transcript.call_id == call_id,
        Transcript.is_final == True
    ).order_by(Transcript.timestamp).all()
    
    if not transcripts:
        raise HTTPException(status_code=404, detail="No transcript found for this call")
    
    entries = [
        TranscriptEntry(
            speaker=t.speaker,
            text=t.text,
            confidence=t.confidence,
            timestamp=t.timestamp,
            is_final=t.is_final
        )
        for t in transcripts
    ]
    
    return TranscriptResponse(
        call_id=call_id,
        entries=entries
    )
