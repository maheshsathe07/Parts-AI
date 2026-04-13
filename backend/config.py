from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str
    youtube_api_key: str
    serpapi_key: str          # https://serpapi.com — replaces Google CSE
    databricks_token: str     # Databricks AI Gateway token
    port: int = 3001

    class Config:
        env_file = ".env"


settings = Settings()