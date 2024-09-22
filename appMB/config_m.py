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
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, mode='w'), stream_handler])  # mode='w', 'a'


# =====================================================================
# =====================================================================
# =====================================================================
# @classmethod
# def get_web_server_port(cls) -> int | None:
#     """
#     Увеличение счетчика порта
#     :return: новый веб сервер порт для бота
#     """
#
#     while True:
#         cls.web_server_port += 1
#         # Сделать здесь проверку на то, что порт не занят (ss -nultp |grep порт)
#         print("+++++======== cls.web_server_port :", cls.web_server_port)
#         break
#     return cls.web_server_port
# =====================================================================
# =================================================
# ============= from .env_manage ==================
# DATABASE_URL_SQLITE="sqlite+pysqlite:///./DB/mb.db"
# DATABASE_URL_SQLITE="sqlite+pysqlite:///mb.db"
# === For Postgres ====
# DB_HOST=localhost
# DB_PORT=5432
# DB_USER=postgres
# DB_PASS=1
# DB_NAME=mb
# =====================================================
# BASE_WEBHOOK_URL="https://178.204.228.105:8443"
# TOKEN_TG=6611111111:AAHbuxxxxxxxJqGJnJQ
# WEB_SERVER_PORT=15001
# =====================================================
# SELF_SSL=True
# =====================================================
# =================================================
# import os
# from dotenv import load_dotenv
# =================================================
# BASE_WEBHOOK_URL: str | None
# BASE_WEBHOOK_URL: str | None = "https://178.1.1.1:8443"
# =================================================
# public_ip = config_Manage.PUBLIC_IP
# print("+++++1++++ public_ip++++++++ ", public_ip)
# if config_Manage.SELF_SSL or not public_ip:
#   public_ip = requests.get('https://api.ipify.org').text
#   config_Manage.PUBLIC_IP = public_ip
# ---------
# BASE_WEBHOOK_URL = f"https://{public_ip}:8443"
# WEBHOOK_SSL_CERT = "/etc/ssl/nginx/" + public_ip + ".self.crt"
# WEBHOOK_SSL_PRIV = "/etc/ssl/nginx/" + public_ip + ".self.key"
# print("+++++++2++++BASE_WEBHOOK_URL +++", BASE_WEBHOOK_URL)
# print("+++++++2++++WEBHOOK_SSL_CERT +++", WEBHOOK_SSL_CERT)
# =================================================
    # BASE_WEBHOOK_URL: str
# =================================================
# @classmethod
# def get_ip_ssl(cls, self_ssl: bool) -> str:
#     """
#     Получение внешнего IP.
#     :param self_ssl: True or False - Использовать самоподписанный сертификат.
#     :return: public_ip: str or None - Внешний IP адрес.
#     """
#
#     load_dotenv(dotenv_path="app/.env_manage")
#     # self_ssl = os.getenv("SELF_SSL")
#     public_ip = os.getenv('PUBLIC_IP')
#     print("--1----- public_ip -------", public_ip)
#     print("------- self_ssl -------", self_ssl)
#     if self_ssl:
#         public_ip = requests.get('https://api.ipify.org').text
#
#     print("--2----- public_ip -------", public_ip)
#
#     return public_ip
# =================================================

# def get_ip_ssl(self_ssl: bool) -> str:
#     """
#     Получение внешнего IP.
#     :param self_ssl: True or False - Использовать самоподписанный сертификат.
#     :return: public_ip: str or None - Внешний IP адрес.
#     """
#
#     load_dotenv(dotenv_path="app/.env_manage")
#     # self_ssl = os.getenv("SELF_SSL")
#     public_ip = os.getenv('PUBLIC_IP')
#     print("--1----- public_ip -------", public_ip)
#     print("------- self_ssl -------", self_ssl)
#     if self_ssl:
#         public_ip = requests.get('https://api.ipify.org').text
#
#     print("--2----- public_ip -------", public_ip)
#
#     return public_ip
# =================================================
# public_ip, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV = "", "", ""
# if self_ssl:
#     public_ip = requests.get('https://api.ipify.org').text
#     # public_ip = "178.204.228.105"  # убрать в реальном проекте (Сертификат делается заранее)
#     # print(f"=== IP Address === {public_ip=}")
#     # WEBHOOK_SSL_CERT = "/etc/ssl/nginx/" + public_ip + ".self.crt"
#     # WEBHOOK_SSL_PRIV = "/etc/ssl/nginx/" + public_ip + ".self.key"
# return public_ip
# # return {"public_ip": public_ip,
# #         "WEBHOOK_SSL_CERT": WEBHOOK_SSL_CERT,
# #         "WEBHOOK_SSL_PRIV": WEBHOOK_SSL_PRIV}
# =================================================
# =================================================
# print("=== Настройки: ===")
# [print(i) for i in config_Manage]


# ===============================
# from pydantic import SecretStr
# ===============================
