from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту


@dataclass
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN')
        ),
        db=DbConfig(
            host=env('POSTGRES_HOST', 'localhost'),
            port=env.int('POSTGRES_PORT', 5432),
            user=env('POSTGRES_USER'),
            password=env('POSTGRES_PASSWORD'),
            database=env('POSTGRES_DB')
        )
    )
