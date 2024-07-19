from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    google_client_id: str
    google_client_secret: str
    
    secret_key: str
    
    weather_api_key: str

    naver_open_api_client_id: str
    naver_open_api_client_secret: str

    kakao_api_key: str
    
    openai_api_key: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()