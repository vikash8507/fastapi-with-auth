from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_VERIFICATION_TOKEN: str
    JWT_RESET_TOKEN: str
    ALGORITHM: str

    model_config = SettingsConfigDict(env_file=".env")
