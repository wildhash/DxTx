from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class CallStatus(str, enum.Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CallDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Call(Base):
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(255), unique=True, index=True, nullable=False)
    direction = Column(SQLEnum(CallDirection), nullable=False)
    status = Column(SQLEnum(CallStatus), default=CallStatus.INITIATED)
    
    # Contact Information
    phone_number = Column(String(50), nullable=False)
    patient_name = Column(String(255))
    
    # Call Details
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    answered_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Transcript & AI Data
    transcript = Column(Text)
    ai_summary = Column(Text)
    conversation_state = Column(JSON)
    extracted_data = Column(JSON)  # Structured patient intake data
    
    # Metadata
    recording_url = Column(String(512))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String(255), index=True, nullable=False)
    
    # Transcript Entry
    speaker = Column(String(50))  # 'agent' or 'patient'
    text = Column(Text, nullable=False)
    confidence = Column(Integer)  # 0-100
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_final = Column(Boolean, default=False)
    
    # Audio segment reference
    audio_start_ms = Column(Integer)
    audio_end_ms = Column(Integer)


class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Patient Information (Encrypted in production)
    phone_number = Column(String(50), unique=True, index=True)
    name = Column(String(255))
    date_of_birth = Column(String(50))  # Encrypted
    
    # Medical Information
    medical_history = Column(JSON)
    current_medications = Column(JSON)
    allergies = Column(JSON)
    
    # Contact & Insurance
    email = Column(String(255))
    address = Column(Text)
    insurance_info = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_contact = Column(DateTime(timezone=True))


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Action Details
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    
    # User/System
    user_id = Column(String(255))
    ip_address = Column(String(50))
    user_agent = Column(String(512))
    
    # Details
    details = Column(JSON)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
