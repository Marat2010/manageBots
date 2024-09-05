"""
Запуск приложения Менеджер ботов:
uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload
"""

import os
import sys
from fastapi import Depends, FastAPI, Body, HTTPException, APIRouter

from .config_manage import (config_Manage, logging, BASE_WEBHOOK_URL,
                            WEBHOOK_SSL_CERT, WEBHOOK_SSL_KEY)
from .routers import bots
from .database import create_tables
from .utils import prepare_Nginx
from fastapi.logger import logger as fastapi_logger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # added path "/home/marat/PycharmProjects/manageBots/app"

# Создаем таблицы, если их нет (раскомментировать)
create_tables()

# ============ Nginx =============================
# Предварительная подготовка Nginx сервера:
# 1. Подготовка самоподписанных ssl сертификатов
# 2. Предварительная подготовка Nginx конфигурации
prepare_Nginx()  # Раскомментировать при первом запуске


# ========== FastAPI ================
app = FastAPI(
    title='Система управления ботами - СУБота©',
    description='API - Менеджер ботов СУБота©️ (manageBots)',
    # title='API - Менеджер ботов',
    # description='Система управления ботами - СУБота&#169;',
    # logging=fastapi_logger
)

app.include_router(bots.router)

logging.info(f"=== Настройки: ===")
logging.info(f"{BASE_WEBHOOK_URL= }")
logging.info(f"{WEBHOOK_SSL_CERT= }")
logging.info(f"{WEBHOOK_SSL_KEY= }")
[logging.info(f"{param}") for param in config_Manage]


# ==================================================
# ==================================================
# title = 'Система управления ©️ботами\n - \U000000A9СУБота©️ &#169;',
# # ========== FastAPI Logs================
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# stream_handler = logging.StreamHandler(sys.stdout)
# log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
# stream_handler.setFormatter(log_formatter)
# logger.addHandler(stream_handler)
#
# logger.info('API is starting up')

# gunicorn_error_logger = logging.getLogger("gunicorn.error")
# gunicorn_logger = logging.getLogger("gunicorn")
# # uvicorn_access_logger = logging.getLogger("uvicorn.access")
# uvicorn_access_logger = logging.getLogger("manageBots.log")
# uvicorn_access_logger.handlers = gunicorn_error_logger.handlers
#
# # fastapi_logger.handlers = gunicorn_error_logger.handlers
# fastapi_logger.handlers = uvicorn_access_logger.handlers
#
# fastapi_logger.setLevel(uvicorn_access_logger.level)
# # if __name__ != "__main__":
# #     fastapi_logger.setLevel(uvicorn_access_logger.level)
# # else:
# #     fastapi_logger.setLevel(logging.DEBUG)


# ======================================
# Запуск приложения:
# uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload
# ======================================
# ======================================
# ======================================
# print("=== Настройки: ===")
# print(f"{BASE_WEBHOOK_URL=}")
# print(f"{WEBHOOK_SSL_CERT=}")
# print(f"{WEBHOOK_SSL_KEY=}")
# [print(i) for i in config_Manage]
# ======================================
# # Скрипт формирования self-signed SSL сертификатов:
# ssl = "./Scripts/ssl.sh " + public_ip
# # Скрипт подготовки предварительной Nginx конфигурации:
# nginx = "./Scripts/nginx.sh " + public_ip
# ======================================