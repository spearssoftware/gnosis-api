from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gnosis_db_path: Path = Path("data/gnosis.db")
    keys_db_path: Path = Path("data/keys.db")
    usearch_index_path: Path = Path("data/gnosis.usearch")
    api_key_salt: str = "gnosis-default-salt-change-me"
    rate_limit_daily: int = 1000
    rate_limit_daily_paid: int = 10000
    rate_limit_burst: int = 10
    rate_limit_burst_paid: int = 30
    rate_limit_burst_window: float = 1.0
    rate_limit_ip: int = 60
    rate_limit_ip_window: float = 60.0

    model_config = {"env_prefix": "GNOSIS_"}


settings = Settings()
