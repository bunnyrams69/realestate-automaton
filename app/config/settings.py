"""
Application Configuration Settings
Uses pydantic-settings to validate environment variables with type safety.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # 1. Application Core
    APP_NAME: str = "Real Estate AI Sales & Marketing Automation"
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "default-insecure-secret-key-change-in-production"
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    WEBHOOK_BASE_URL: str = "https://app-dsl-determine-translation.trycloudflare.com"
    TIMEZONE: str = "Asia/Kolkata"

    # Image Library Configuration
    IMAGE_LIBRARY_PATH: str = "images_lib"

    # Cal.com Booking Configuration
    CAL_COM_API_KEY: str = ""
    CAL_COM_EVENT_TYPE_ID: str = ""
    CAL_COM_BOOKING_URL: str = "https://cal.com/gunda-ganesh-ofduvx/site-visit"

    # Broker & Notification Info
    BROKER_NAME: str = "Prestige Realty Sales Team"
    BROKER_PHONE: str = "+91 90000 00000"

    # 2. OpenRouter & AI Model Orchestration (Replaces Direct Claude API)
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API Key")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="OpenRouter API Base URL")
    OPENROUTER_MODEL: str = Field(default="openrouter/auto", description="Primary reasoning & extraction model")
    OPENROUTER_FAST_MODEL: str = Field(default="openrouter/auto", description="Fast lightweight intent routing model")
    OPENROUTER_MAX_TOKENS: int = 1024
    OPENROUTER_TEMPERATURE: float = 0.2

    # Anthropic / Claude API (Fallback compatibility)
    ANTHROPIC_API_KEY: str = "sk-ant-placeholder"
    CLAUDE_MODEL: str = "claude-3-7-sonnet-20250219"
    CLAUDE_FAST_MODEL: str = "claude-3-5-haiku-20241022"
    CLAUDE_MAX_TOKENS: int = 1024
    CLAUDE_TEMPERATURE: float = 0.2

    # 3. WhatsApp Business Cloud API
    WHATSAPP_VERIFY_TOKEN: str = "placeholder-verify-token"
    WHATSAPP_APP_SECRET: str = "placeholder-app-secret"
    WHATSAPP_PHONE_NUMBER_ID: str = "placeholder-phone-number-id"
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = "placeholder-waba-id"
    WHATSAPP_API_TOKEN: str = "placeholder-whatsapp-api-token"
    WHATSAPP_API_VERSION: str = "v21.0"

    # 4. Database (PostgreSQL / Supabase)
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"  # Defaults to local fallback if DB not configured
    SYNC_DATABASE_URL: str = "sqlite:///./test.db"
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # 5. Google Calendar API
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = "credentials/google-calendar-service-account.json"
    GOOGLE_CALENDAR_ID: str = "primary"
    DEFAULT_SITE_VISIT_DURATION_MINUTES: int = 45

    # 6. Meta Marketing API
    META_ACCESS_TOKEN: str = ""
    META_AD_ACCOUNT_ID: str = ""

    # 7. Business Logic & Qualification Thresholds
    LEAD_SCORE_HOT_THRESHOLD: int = 75
    LEAD_SCORE_WARM_THRESHOLD: int = 45
    DEFAULT_FOLLOW_UP_INTERVAL_HOURS: int = 24
    MAX_FOLLOW_UP_ATTEMPTS: int = 4
    ENABLE_HUMAN_HANDOFF_NOTIFICATION: bool = True
    ADMIN_NOTIFICATION_EMAIL: str = "sales-lead@example.com"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


# Singleton instance for application access
settings = Settings()
