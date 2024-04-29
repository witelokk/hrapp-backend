from functools import cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_username: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    secret_key: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


@cache
def get_settings():
    return Settings()
