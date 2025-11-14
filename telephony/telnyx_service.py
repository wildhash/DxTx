import telnyx
from app.config import settings
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize Telnyx
telnyx.api_key = settings.TELNYX_API_KEY


class TelnyxService:
    """Service for handling Telnyx telephony operations"""
    
    def __init__(self):
        self.app_id = settings.TELNYX_APP_ID
        self.phone_number = settings.TELNYX_PHONE_NUMBER
    
    async def initiate_call(
        self,
        to_phone: str,
        from_phone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate an outbound call via Telnyx
        
        Args:
            to_phone: Phone number to call (E.164 format)
            from_phone: Caller ID phone number (optional)
        
        Returns:
            Call details including call_control_id
        """
        try:
            from_number = from_phone or self.phone_number
            
            call = telnyx.Call.create(
                connection_id=self.app_id,
                to=to_phone,
                from_=from_number,
                webhook_url=f"{settings.API_HOST}/webhooks/telnyx",
                stream_url=f"wss://{settings.API_HOST}/stream/audio",
                stream_track="both_tracks"  # Record both sides
            )
            
            logger.info(f"Initiated call to {to_phone}, call_control_id: {call.call_control_id}")
            
            return {
                "call_control_id": call.call_control_id,
                "call_leg_id": call.call_leg_id,
                "call_session_id": call.call_session_id,
                "to": to_phone,
                "from": from_number,
                "status": "initiated"
            }
        
        except Exception as e:
            logger.error(f"Error initiating call: {e}")
            raise
    
    async def answer_call(self, call_control_id: str) -> Dict[str, Any]:
        """Answer an inbound call"""
        try:
            result = telnyx.Call.answer(
                call_control_id=call_control_id,
                webhook_url=f"{settings.API_HOST}/webhooks/telnyx"
            )
            
            logger.info(f"Answered call: {call_control_id}")
            return {"status": "answered", "call_control_id": call_control_id}
        
        except Exception as e:
            logger.error(f"Error answering call: {e}")
            raise
    
    async def hangup_call(self, call_control_id: str) -> Dict[str, Any]:
        """Hang up a call"""
        try:
            result = telnyx.Call.hangup(call_control_id=call_control_id)
            logger.info(f"Hung up call: {call_control_id}")
            return {"status": "hung_up", "call_control_id": call_control_id}
        
        except Exception as e:
            logger.error(f"Error hanging up call: {e}")
            raise
    
    async def send_audio(
        self,
        call_control_id: str,
        audio_url: str
    ) -> Dict[str, Any]:
        """
        Send audio to an active call (for TTS playback)
        
        Args:
            call_control_id: The call control ID
            audio_url: URL of the audio file to play
        """
        try:
            result = telnyx.Call.playback_start(
                call_control_id=call_control_id,
                audio_url=audio_url
            )
            
            logger.info(f"Playing audio to call: {call_control_id}")
            return {"status": "playing", "call_control_id": call_control_id}
        
        except Exception as e:
            logger.error(f"Error sending audio: {e}")
            raise
    
    async def start_recording(self, call_control_id: str) -> Dict[str, Any]:
        """Start recording a call"""
        try:
            result = telnyx.Call.recording_start(
                call_control_id=call_control_id,
                format="wav",
                channels="dual"
            )
            
            logger.info(f"Started recording call: {call_control_id}")
            return {"status": "recording", "call_control_id": call_control_id}
        
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            raise
    
    async def stop_recording(self, call_control_id: str) -> Dict[str, Any]:
        """Stop recording a call"""
        try:
            result = telnyx.Call.recording_stop(call_control_id=call_control_id)
            logger.info(f"Stopped recording call: {call_control_id}")
            return {"status": "stopped", "call_control_id": call_control_id}
        
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            raise


# Singleton instance
telnyx_service = TelnyxService()
