import httpx
from app.config import settings
import logging
from typing import Optional
import base64
import io

logger = logging.getLogger(__name__)


class ElevenLabsTTSService:
    """
    ElevenLabs text-to-speech service (primary)
    """
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID
        self.api_url = "https://api.elevenlabs.io/v1"
        self.client = httpx.AsyncClient()
    
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice_id: Optional voice ID (uses default if not provided)
            
        Returns:
            Audio data as bytes
        """
        try:
            selected_voice = voice_id or self.voice_id
            
            response = await self.client.post(
                f"{self.api_url}/text-to-speech/{selected_voice}",
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model_id": "eleven_turbo_v2",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                        "style": 0.5,
                        "use_speaker_boost": True
                    }
                }
            )
            
            if response.status_code == 200:
                logger.info(f"ElevenLabs TTS successful for text: {text[:50]}...")
                return response.content
            else:
                logger.error(f"ElevenLabs TTS failed: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error with ElevenLabs TTS: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class DeepgramTTSService:
    """
    Deepgram text-to-speech service (fallback)
    """
    
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY
        self.api_url = "https://api.deepgram.com/v1"
        self.client = httpx.AsyncClient()
    
    async def synthesize(self, text: str) -> Optional[bytes]:
        """
        Synthesize speech from text using Deepgram
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes
        """
        try:
            response = await self.client.post(
                f"{self.api_url}/speak",
                headers={
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json"
                },
                params={
                    "model": "aura-asteria-en"  # Warm, conversational voice
                },
                json={
                    "text": text
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Deepgram TTS successful for text: {text[:50]}...")
                return response.content
            else:
                logger.error(f"Deepgram TTS failed: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error with Deepgram TTS: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class TTSManager:
    """
    Manager that coordinates between primary and fallback TTS services
    """
    
    def __init__(self):
        self.primary = ElevenLabsTTSService()
        self.fallback = DeepgramTTSService()
        self.use_fallback = False
    
    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Synthesize speech using primary service with fallback
        
        Args:
            text: Text to synthesize
            voice_id: Optional voice ID for ElevenLabs
            
        Returns:
            Audio data as bytes
        """
        # Try primary service first
        if not self.use_fallback:
            audio_data = await self.primary.synthesize(text, voice_id)
            if audio_data:
                return audio_data
            
            # If primary fails, switch to fallback
            logger.warning("ElevenLabs TTS failed, switching to Deepgram fallback")
            self.use_fallback = True
        
        # Use fallback service
        return await self.fallback.synthesize(text)
    
    async def close(self):
        """Close all services"""
        await self.primary.close()
        await self.fallback.close()


# Singleton instance
tts_manager = TTSManager()
