from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class _Settings(BaseSettings):
    # General
    name_mapping: dict[str, str]

    # Telegram
    telegram_api_token: str

    # Transmission
    transmission_host: str
    transmission_port: int
    transmission_username: str
    transmission_password: str

    model_config = SettingsConfigDict(env_file='.env')

    @computed_field()
    @property
    def users(self) -> list[str]:
        return list(self.name_mapping.keys())


settings = _Settings()
