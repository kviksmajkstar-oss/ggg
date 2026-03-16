from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OneMusic AI"
    database_url: str = "sqlite:///./onemusic.db"
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    soundcloud_client_id: str = ""
    ytmusic_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
