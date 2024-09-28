import logging
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger("UniSwapBot")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class DatabaseConfig(BaseModel):
    dialect: str
    driver: str
    username: str
    password: str
    host: str
    port: str
    database: str

    @property
    def url(self) -> str:
        return f"{self.dialect}+{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseModel):
    host: str
    port: int
    password: str
    db: int
    ssl: bool
    timeout: int

    @property
    def url(self) -> str:
        scheme = "rediss" if self.ssl else "redis"
        auth_part = f":{self.password}@" if self.password else ""
        return f"{scheme}://{auth_part}{self.host}:{self.port}/{self.db}"


class UniSwapConfig(BaseModel):
    api_key: str
    subgraph_id: str


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", case_sensitive=False, extra="ignore"
    )

    db: DatabaseConfig
    uniswap: UniSwapConfig
    redis: RedisConfig

    telegram_bot_token: str


settings = Config()
