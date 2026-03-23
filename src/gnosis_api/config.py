from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gnosis_db_path: Path = Path("data/gnosis.db")
    keys_db_path: Path = Path("data/keys.db")
    api_key_salt: str = "gnosis-default-salt-change-me"
    rate_limit_daily: int = 1000
    rate_limit_daily_paid: int = 10000

    model_config = {"env_prefix": "GNOSIS_"}


settings = Settings()
