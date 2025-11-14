from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class CallStatus(str, Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CallDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallCreate(BaseModel):
    phone_number: str = Field(..., description="Phone number to call")
    patient_name: Optional[str] = None


class CallResponse(BaseModel):
    id: int
    call_id: str
    direction: CallDirection
    status: CallStatus
    phone_number: str
    patient_name: Optional[str] = None
    started_at: datetime
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None
    ai_summary: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class TranscriptEntry(BaseModel):
    speaker: str
    text: str
    confidence: Optional[int] = None
    timestamp: datetime
    is_final: bool = False


class TranscriptResponse(BaseModel):
    call_id: str
    entries: List[TranscriptEntry]


class CallSummary(BaseModel):
    total_calls: int
    active_calls: int
    completed_calls: int
    failed_calls: int


class WebhookEvent(BaseModel):
    event_type: str
    call_id: str
    data: Dict[str, Any]


class OutboundCallRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to call (E.164 format)")
    patient_name: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context for the AI agent"
    )


class ConversationState(BaseModel):
    current_step: str
    collected_data: Dict[str, Any]
    next_questions: List[str]
    sentiment: Optional[str] = None
