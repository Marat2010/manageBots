import logging

import requests
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ======= DB =======
    DATABASE_URL_SQLITE: str = "sqlite+pysqlite:///./DB/manbot.db"

    # === Telegram settings for bots ===
    SELF_SSL: bool = True  # Для случаев, когда нет нормального сертификата на домен или IP
    PUBLIC_IP: str | None = None  # Внешний IP адрес
    APP_PORT: int = 8900  # Локальный порт для приложения API

    WEBHOOK_PATH: str = "/bot/"  # Часть полного пути вебхук урла (BASE_WEBHOOK_URL + WEBHOOK_PATH + токен)
    WEBHOOK_SECRET: str = "chaNge_secreT2024"  # Безопасность (входящие запросы исходят от ТГ сервера).
    # Недопустимые символы @,$,&,.. Разрешены только символы A-Z, a-z, 0-9, _и -.

    # ===== default value for manage =====
    WEB_SERVER_HOST: str = "127.0.0.1"  # IP адрес, локально запущенного бота (функционал)
    START_WEB_SERVER_PORT: int = 9000  # Начальный порт для ботов. (Для каждого нового бота номер увеличвается на '+1')

    # ===== Log file name =====
    LOG_MANAGE: str = "manageBots.log"

    # Начиная со второй версии pydantic, настройки класса настроек задаются через model_config.
    # Будем использовать файл ".env_manage", который будет прочитан с кодировкой UTF-8.
    model_config = SettingsConfigDict(env_file='appMB/.env_m', env_file_encoding='utf-8', extra='ignore')
    # ДАННЫЕ БЕРУТСЯ СНАЧАЛА из переменных окружения ОС, если их там нет, то из файла ".env_manage",
    # если и там нет, то берутся отсюда значения по умолчанию (SELF_SSL: bool = True)


config_M = Settings()


if not config_M.PUBLIC_IP:
    config_M.PUBLIC_IP = requests.get('https://api.ipify.org').text
    print(config_M.PUBLIC_IP)


BASE_WEBHOOK_URL = f"https://{config_M.PUBLIC_IP}:8443"
WEBHOOK_SSL_CERT = "/etc/ssl/nginx/" + config_M.PUBLIC_IP + ".self.crt"
WEBHOOK_SSL_KEY = "/etc/ssl/nginx/" + config_M.PUBLIC_IP + ".self.key"

# ========= LOGS =============================
LOG_FILE = config_M.LOG_MANAGE
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, mode='w'), stream_handler])  # mode='w', 'a'


# =====================================================================
# =====================================================================

