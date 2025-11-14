from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Call, Transcript, CallStatus
from agents.state_machine import ConversationStateMachine
from agents.empathetic_agent import empathetic_agent
from app.services.transcription import transcription_manager
from app.services.tts import tts_manager
from telephony.telnyx_service import telnyx_service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/telnyx")
async def telnyx_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle Telnyx webhooks for call events
    """
    try:
        payload = await request.json()
        
        event_type = payload.get("data", {}).get("event_type")
        call_control_id = payload.get("data", {}).get("payload", {}).get("call_control_id")
        
        logger.info(f"Received Telnyx webhook: {event_type}, call_control_id: {call_control_id}")
        
        # Find the call in database
        call = db.query(Call).filter(
            Call.conversation_state["telnyx_call_control_id"].astext == call_control_id
        ).first()
        
        if not call:
            logger.warning(f"Call not found for control ID: {call_control_id}")
            return {"status": "ok"}
        
        # Handle different event types
        if event_type == "call.initiated":
            call.status = CallStatus.INITIATED
            
        elif event_type == "call.ringing":
            call.status = CallStatus.RINGING
            
        elif event_type == "call.answered":
            call.status = CallStatus.ANSWERED
            call.answered_at = datetime.now()
            
            # Start the conversation
            await handle_call_answered(call, call_control_id, db)
            
        elif event_type == "call.hangup":
            call.status = CallStatus.COMPLETED
            call.ended_at = datetime.now()
            
            if call.answered_at:
                call.duration_seconds = int((call.ended_at - call.answered_at).total_seconds())
            
            # Generate AI summary
            await generate_call_summary(call, db)
        
        elif event_type == "call.speak.ended":
            # Agent finished speaking, ready for patient response
            pass
        
        db.commit()
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error handling Telnyx webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_call_answered(call: Call, call_control_id: str, db: Session):
    """
    Handle when a call is answered - start the conversation
    """
    try:
        # Initialize or load conversation state machine
        state_machine_data = call.conversation_state.get("state_machine", {})
        state_machine = ConversationStateMachine(state_machine_data)
        
        # Get the greeting prompt
        greeting = state_machine.get_current_prompt()
        
        # Generate empathetic greeting using AI
        ai_greeting = await empathetic_agent.generate_response(
            conversation_history=[],
            current_prompt=greeting,
            user_input="",
            context={"is_greeting": True}
        )
        
        # Synthesize speech
        audio_data = await tts_manager.synthesize_speech(ai_greeting or greeting)
        
        if audio_data:
            # TODO: Upload audio to temporary storage and get URL
            # For now, we'll use Telnyx's speak command which accepts text
            # In production, you'd upload the audio and use playback_start
            pass
        
        # Update conversation state
        call.conversation_state["state_machine"] = state_machine.get_state()
        db.commit()
        
        logger.info(f"Started conversation for call {call.call_id}")
    
    except Exception as e:
        logger.error(f"Error handling call answered: {e}")


async def generate_call_summary(call: Call, db: Session):
    """
    Generate AI summary when call ends
    """
    try:
        state_machine_data = call.conversation_state.get("state_machine", {})
        conversation_history = state_machine_data.get("conversation_history", [])
        collected_data = state_machine_data.get("collected_data", {})
        
        # Generate summary using AI
        summary = await empathetic_agent.generate_summary(
            conversation_history=conversation_history,
            collected_data=collected_data
        )
        
        call.ai_summary = summary
        call.extracted_data = collected_data
        db.commit()
        
        logger.info(f"Generated summary for call {call.call_id}")
    
    except Exception as e:
        logger.error(f"Error generating call summary: {e}")


@router.post("/transcription")
async def transcription_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handle real-time transcription webhooks
    """
    try:
        payload = await request.json()
        
        call_id = payload.get("call_id")
        text = payload.get("text")
        speaker = payload.get("speaker", "patient")
        is_final = payload.get("is_final", False)
        confidence = payload.get("confidence", 100)
        
        # Find the call
        call = db.query(Call).filter(Call.call_id == call_id).first()
        
        if not call:
            return {"status": "ok"}
        
        # Store transcript entry
        transcript = Transcript(
            call_id=call_id,
            speaker=speaker,
            text=text,
            confidence=confidence,
            is_final=is_final
        )
        
        db.add(transcript)
        
        # If this is a final patient response, process it with AI
        if is_final and speaker == "patient":
            await process_patient_response(call, text, db)
        
        db.commit()
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error handling transcription webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_patient_response(call: Call, patient_text: str, db: Session):
    """
    Process patient response with AI and advance conversation
    """
    try:
        # Load state machine
        state_machine_data = call.conversation_state.get("state_machine", {})
        state_machine = ConversationStateMachine(state_machine_data)
        
        current_step = state_machine.current_step.value
        
        # Extract information from patient response
        extracted_data = await empathetic_agent.extract_information(
            user_input=patient_text,
            expected_field=current_step.replace("_collection", "").replace("_", "")
        )
        
        # Detect sentiment
        sentiment = await empathetic_agent.detect_sentiment(patient_text)
        
        # Generate empathetic response
        ai_response = await empathetic_agent.generate_response(
            conversation_history=state_machine.conversation_history,
            current_prompt=state_machine.get_current_prompt(),
            user_input=patient_text,
            context={"sentiment": sentiment}
        )
        
        # Advance conversation
        state_machine.advance(patient_text, extracted_data)
        
        # Get next prompt
        next_prompt = state_machine.get_current_prompt()
        
        # Combine response and next question
        full_response = f"{ai_response} {next_prompt}"
        
        # Synthesize and play response
        audio_data = await tts_manager.synthesize_speech(full_response)
        
        # Update call state
        call.conversation_state["state_machine"] = state_machine.get_state()
        call.conversation_state["last_sentiment"] = sentiment
        
        db.commit()
        
        logger.info(f"Processed patient response for call {call.call_id}")
    
    except Exception as e:
        logger.error(f"Error processing patient response: {e}")
