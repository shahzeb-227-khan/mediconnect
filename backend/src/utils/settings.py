from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int = 5432
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str | None = None

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    ORIGIN_URL: str
    CORS_ORIGINS: str | None = None
    EMAIL_VERIFICATION_ENABLED: bool = True

    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    STRIPE_SECRET_KEY: str
    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    GEMINI_API_KEY: str

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if not all((self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME)):
            raise ValueError(
                "Set DATABASE_URL or DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME."
            )
        return (
            f"postgresql+psycopg2://{quote_plus(self.DB_USER)}:"
            f"{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )


settings = Settings()