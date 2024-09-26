"""
Запуск приложения Менеджер ботов:
uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload
"""

import os
import sys

import uvicorn
from fastapi import FastAPI

from appMB.config_m import (config_M, logging, BASE_WEBHOOK_URL,
                            WEBHOOK_SSL_CERT, WEBHOOK_SSL_KEY)

from appMB.routers import router, add_first_urls
from appMB.database import create_tables


sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # added path "/home/marat/PycharmProjects/manageBots/app"


# ========== FastAPI ================
app = FastAPI(
    title='Система управления ботами - СУБота©',
    description='API - Менеджер ботов СУБота©️ (manageBots)',
)


@app.on_event("startup")
def on_startup():
    create_tables()  # Создаем таблицы
    add_first_urls()  # добваление в базу первого вебхук урла (BASE_WEBHOOK_URL)


app.include_router(router)

logging.warning(f"=== Настройки manageBots: ===")
logging.warning(f"{BASE_WEBHOOK_URL= }")
logging.warning(f"{WEBHOOK_SSL_CERT= }")
logging.warning(f"{WEBHOOK_SSL_KEY= }")
[logging.warning(f"{param}") for param in config_M]


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=config_M.APP_PORT, log_level="info", reload=True)

# Запуск 2 с терминала:
# uvicorn appMB.main:app --host 127.0.0.1 --port 8090 --reload

print("============ E N D ============")


# ==========================================================
# ==========================================================
# Запуск через systemd (без "--reload"):
# ExecStart=/usr/bin/bash -c ('cd /root/manageBots && source .venv/bin/activate && .venv/bin/uvicorn'
#                             ' appMB.main:app --host 127.0.0.1 --port 8900')
# ==========================================================
# "--reload" убрать в рабочем проекте, т.к. будет идти перезапуск при каждом добвалении и удалении
# бота (т.к. меняется отслеживаемвая в проекте папка "our_Bots/..")
# ==========================================================
