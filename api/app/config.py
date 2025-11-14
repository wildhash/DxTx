from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_SECRET_KEY: str = "your-secret-key-change-this"
    
    # Database
    DATABASE_URL: str = "postgresql://dxtx_user:dxtx_password@localhost:5432/dxtx_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Telnyx
    TELNYX_API_KEY: str = ""
    TELNYX_PUBLIC_KEY: str = ""
    TELNYX_APP_ID: str = ""
    TELNYX_PHONE_NUMBER: str = ""
    
    # TwinMind (Primary Transcription)
    TWINMIND_API_KEY: str = ""
    TWINMIND_API_URL: str = "https://api.twinmind.ai/v1"
    
    # Deepgram (Fallback Transcription & TTS)
    DEEPGRAM_API_KEY: str = ""
    
    # ElevenLabs (Primary TTS)
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = ""
    
    # OpenAI (LLM)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Security & HIPAA
    ENCRYPTION_KEY: str = "your-encryption-key-32-chars-min"
    AUDIT_LOG_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 2555  # 7 years for HIPAA
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
