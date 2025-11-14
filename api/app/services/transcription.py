import httpx
from app.config import settings
import logging
from typing import Dict, Any, Optional
import asyncio

logger = logging.getLogger(__name__)


class TwinMindTranscriptionService:
    """
    TwinMind real-time transcription service
    """
    
    def __init__(self):
        self.api_key = settings.TWINMIND_API_KEY
        self.api_url = settings.TWINMIND_API_URL
        self.client = httpx.AsyncClient()
    
    async def start_transcription(self, audio_stream_url: str) -> Dict[str, Any]:
        """
        Start real-time transcription of audio stream
        
        Args:
            audio_stream_url: URL or reference to audio stream
            
        Returns:
            Transcription session details
        """
        try:
            response = await self.client.post(
                f"{self.api_url}/transcribe/stream",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "audio_source": audio_stream_url,
                    "language": "en",
                    "enable_diarization": True,  # Separate speakers
                    "enable_punctuation": True,
                    "interim_results": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Started TwinMind transcription session: {result.get('session_id')}")
                return result
            else:
                logger.error(f"TwinMind transcription failed: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error starting TwinMind transcription: {e}")
            return None
    
    async def transcribe_audio_chunk(
        self,
        audio_data: bytes,
        session_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribe an audio chunk
        
        Args:
            audio_data: Raw audio data
            session_id: Optional session ID for continuity
            
        Returns:
            Transcription result
        """
        try:
            response = await self.client.post(
                f"{self.api_url}/transcribe/chunk",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "audio/wav"
                },
                params={"session_id": session_id} if session_id else {},
                content=audio_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "text": result.get("text", ""),
                    "confidence": result.get("confidence", 0),
                    "is_final": result.get("is_final", False),
                    "speaker": result.get("speaker", "unknown")
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error transcribing audio chunk: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class DeepgramTranscriptionService:
    """
    Deepgram transcription service (fallback)
    """
    
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        self.api_url = "https://api.deepgram.com/v1"
        self.client = httpx.AsyncClient()
    
    async def transcribe_audio_chunk(
        self,
        audio_data: bytes,
        encoding: str = "linear16",
        sample_rate: int = 16000
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio using Deepgram
        
        Args:
            audio_data: Raw audio data
            encoding: Audio encoding format
            sample_rate: Audio sample rate
            
        Returns:
            Transcription result
        """
        try:
            response = await self.client.post(
                f"{self.api_url}/listen",
                headers={
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "audio/wav"
                },
                params={
                    "model": "nova-2",
                    "language": "en",
                    "punctuate": "true",
                    "diarize": "true",
                    "smart_format": "true"
                },
                content=audio_data
            )
            
            if response.status_code == 200:
                result = response.json()
                channel = result.get("results", {}).get("channels", [{}])[0]
                alternatives = channel.get("alternatives", [{}])
                
                if alternatives:
                    transcript = alternatives[0].get("transcript", "")
                    confidence = alternatives[0].get("confidence", 0)
                    
                    return {
                        "text": transcript,
                        "confidence": int(confidence * 100),
                        "is_final": True,
                        "speaker": "unknown"
                    }
            
            return None
        
        except Exception as e:
            logger.error(f"Error transcribing with Deepgram: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class TranscriptionManager:
    """
    Manager that coordinates between primary and fallback transcription services
    """
    
    def __init__(self):
        self.primary = TwinMindTranscriptionService()
        self.fallback = DeepgramTranscriptionService()
        self.use_fallback = False
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        session_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio using primary service with fallback
        
        Args:
            audio_data: Raw audio data
            session_id: Optional session ID
            
        Returns:
            Transcription result
        """
        # Try primary service first
        if not self.use_fallback:
            result = await self.primary.transcribe_audio_chunk(audio_data, session_id)
            if result:
                return result
            
            # If primary fails, switch to fallback
            logger.warning("TwinMind transcription failed, switching to Deepgram fallback")
            self.use_fallback = True
        
        # Use fallback service
        return await self.fallback.transcribe_audio_chunk(audio_data)
    
    async def close(self):
        """Close all services"""
        await self.primary.close()
        await self.fallback.close()


# Singleton instance
transcription_manager = TranscriptionManager()
