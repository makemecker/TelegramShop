from dataclasses import dataclass
from environs import Env
from database import DatabaseManager


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admins: list[int]  # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot
    database: DatabaseManager
    delivery_threshold: int


def load_config(path: str | None = '.env') -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOT_TOKEN'),
                               admins=list(map(int, env.list('ADMINS')))),
                  database=DatabaseManager('database/database.db'),
                  delivery_threshold=int(env('DELIVERY_THRESHOLD')))
