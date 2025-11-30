from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Admin Assistant"
    env: str = "dev"
    debug: bool = True

    # PostgreSQL (усі реальні значення тільки з .env / secrets)
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # --- MongoDB ---
    # Готовий URL (має найвищий пріоритет)
    MONGO_URL: str | None = Field(default=None)

    # Частини URL (fallback)
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27020
    MONGO_USER: str | None = None
    MONGO_PASSWORD: str | None = None
    MONGO_DB: str = "assistant_mongo"

    BOT_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def mongo_url(self) -> str:
        # ← 1) Якщо MONGO_URL заданий у .env → ВИКОРИСТОВУЄМО ЙОГО
        if self.MONGO_URL:
            return self.MONGO_URL

        # ← 2) Інакше будуємо зі шматків
        if self.MONGO_USER and self.MONGO_PASSWORD:
            return (
                f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}"
                f"@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"
            )

        return f"mongodb://{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"


settings = Settings()
