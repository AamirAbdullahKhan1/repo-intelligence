"""Local application configuration. No provider or model settings."""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[1] / '.env', extra='ignore')
    data_dir: Path = Path(__file__).resolve().parents[2] / 'data'
    allowed_origins: str = 'http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:5174'

@lru_cache
def get_settings():
    return Settings()
