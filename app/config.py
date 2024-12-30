
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    ES_DB: str = ''
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")



Config = Settings()