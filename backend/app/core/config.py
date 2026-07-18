from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Developer Portfolio API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = ""
    EMAIL_RECIPIENT: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "qwen2.5:7b"
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"

    RATE_LIMIT_MAX_REQUESTS: int = 5
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    METRICS_API_KEY: str = ""

    DATA_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data"

    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    TRUSTED_PROXY: str = ""
    LOG_LEVEL: str = "INFO"

    @property
    def is_production(self) -> bool:
        return not self.DEBUG

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

(settings.DATA_DIR / "logs").mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "metrics").mkdir(parents=True, exist_ok=True)
(settings.DATA_DIR / "emails").mkdir(parents=True, exist_ok=True)
