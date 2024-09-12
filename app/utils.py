import asyncio
import logging
import shlex
import subprocess
from typing import Union, Dict, Any

import requests
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import (TelegramUnauthorizedError, TelegramBadRequest,
                                TelegramNotFound)
from aiogram.types import FSInputFile, User
from aiogram.utils.token import TokenValidationError, validate_token
from fastapi import HTTPException

# from app.models import ActiveBot, BotsOrm
from models import ActiveBot, BotsOrm
from config_manage import config_Manage, BASE_WEBHOOK_URL, WEBHOOK_SSL_CERT

# ========= TG ===============================
SELF_SSL = config_Manage.SELF_SSL
WEBHOOK_PATH = config_Manage.WEBHOOK_PATH
WEBHOOK_SECRET = config_Manage.WEBHOOK_SECRET


# ============ TG =============================
async def set_token(active: bool, token: str) -> User | TelegramUnauthorizedError | TokenValidationError:
    """
    Устанавливает вебхук по токену
    :param active: True - Установить вебхук, False - удалить вебхук
    :param token: Токен телеграмм
    :return: Объект пользователя телеграмма (Информацию о созданном боте)
    """
    aio_session = AiohttpSession()

    try:
        new_bot = Bot(token=token, session=aio_session)
        bot_info = await new_bot.get_me()
        logging.info(f"\n\n  === Бот Инфо: ===\n{bot_info}\n")
    except TelegramUnauthorizedError as e:
        logging.warning(f"\n\n  === Неверный {token= }, Ошибка: '{e}' ===\n")
        raise HTTPException(status_code=422,
                            detail=f"=== Неверный {token= }, Ошибка: '{e}' ===")
    except TokenValidationError as e:
        logging.warning(f"\n\n  === Токен не прошел валидацию {token= }, Ошибка: '{e}' ===\n")
        raise HTTPException(status_code=422,
                            detail=f"=== Токен не прошел валидацию {token= }, Ошибка: '{e}' ===")
    except TelegramNotFound as e:
        logging.warning(f"\n\n  === Вебхук не установлен {token= }, Ошибка: '{e}' ===\n")
        raise HTTPException(status_code=422,
                            detail=f"=== Вебхук не установлен {token= }, Ошибка: '{e}' ===")
    except Exception as e:
        logging.error(f"\n\n  === Неизвестная ошибка! {token= }, Ошибка: '{e}' ===\n")
        raise HTTPException(status_code=422,
                            detail=f"=== Неизвестная ошибка! {token= }, Ошибка: '{e}' ===")
    await new_bot.delete_webhook(drop_pending_updates=True)

    logging.info(f"\n\n  === Удален вебхук для токена: {token}, пользователь: {bot_info.username} ===\n")
    logging.info(f"\n  === {BASE_WEBHOOK_URL=} ===\n")
    logging.info(f"\n  === {WEBHOOK_PATH=} ===\n")
    logging.info(f"\n  === {WEBHOOK_SSL_CERT=} ===\n")
    logging.info(f"\n  === {WEBHOOK_SECRET=} ===\n")

    if active:
        try:
            if SELF_SSL:
                await new_bot.set_webhook(
                    f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}{token}",
                    certificate=FSInputFile(WEBHOOK_SSL_CERT),
                    secret_token=WEBHOOK_SECRET)

                logging.info(f"\n\n  === new_bot.get_webhook_info(): ===\n{await new_bot.get_webhook_info()}\n")
            else:
                await new_bot.set_webhook(
                    f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}{token}",
                    secret_token=WEBHOOK_SECRET)
        except TelegramBadRequest as e:
            logging.error(f"\n\n  === Возможно недопустимый символ (@,$,&,..)."
                          f" Разрешены только символы A-Z, a-z, 0-9, _и -."
                          f" {WEBHOOK_SECRET= }, Ошибка: '{e}' ===\n")
            raise HTTPException(status_code=422,
                                detail=f"=== Возможно недопустимый символ (@,$,&,..)."
                                       f" Разрешены только символы A-Z, a-z, 0-9, _и -."
                                       f" {WEBHOOK_SECRET= }, Ошибка: '{e}' ===")
        except Exception as e:
            logging.error(f"\n\n  === ! Неизвестная ошибка ! {token= }, Ошибка: '{e}' ===\n")
            raise HTTPException(status_code=422,
                                detail=f"=== Неизвестная ошибка! {token= }, Ошибка: '{e}' ===")

        logging.info(f"\n\n  === Установлен вебхук для токена: {token}, пользователь: {bot_info.username} ===\n")

    await new_bot.session.close()
    return bot_info


# def change_state_bot(bot: BotsOrm) -> User | None:
def change_state_bot(bot: BotsOrm) -> User:
    """
    Активация или деактивация бота.
    При активации для локально запушенного бота (функционала бота),
     устанавливаем webhook, при остановке удаляем webhook.
    """
    logging.info(f"\n\n  === Состояние бота: ===\n{bot.active=} \n")
    logging.info(f"\n\n  === Модель Бота: ===\n{bot}\n")

    if bot.active == ActiveBot.Yes:
        # === Установка вебхука ===
        bot_info = asyncio.run(set_token(True, bot.token_tg))

        # === # Добавление бота в конфигурацию Nginx ===
        bot_proc = activate_bot_nginx(bot)  # Добавление бота в конфигурацию Nginx
        if bot_proc.returncode == 1:  # В случае ошибки
            logging.error(f"\n=== ERROR: ===\n{bot_proc.stderr}")
            raise HTTPException(status_code=422,
                                detail=f"=== Бот НЕДОБАВЛЕН в конфигурацию Nginx !!!\n"
                                       f" Ошибки: '{bot_proc.stderr}' ===")
        logging.info(f"\n{bot_proc.stdout}\n")

        return bot_info

    elif bot.active == ActiveBot.No:
        # === Удаление вебхука ===
        bot_info = asyncio.run(set_token(False, bot.token_tg))

        # === # Удаление бота из конфигурации Nginx ===
        bot_proc = activate_bot_nginx(bot)  # Удаление бота из конфигурации Nginx
        if bot_proc.returncode == 1:  # В случае ошибки
            logging.error(f"\n=== ERROR: ===\n{bot_proc.stderr}")
            raise HTTPException(status_code=422,
                                detail=f"=== Не УДАЛОСЬ удалить бота из конфигурации Nginx !!!\n"
                                       f" Ошибки: '{bot_proc.stderr}' ===")
        logging.info(f"\n{bot_proc.stdout}\n")

        return bot_info


# ============ Nginx =============================

def run_com(com_line: str):
    """
    Запуск shell скриптов
    :param com_line: Командная строка для запуска shell скрипта
    :return:
    """
    command_split = shlex.split(com_line)
    logging.info(f"\n  === Командная строка (split): ===\n{command_split}\n")

    proc = subprocess.run(
        command_split,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",)
    return proc


def activate_bot_nginx(bot: BotsOrm):
    activate_bot_scr = (f"./Scripts/activate_bot_nginx.sh {bot.active.name} {config_Manage.WEBHOOK_PATH}"
                        f" {bot.token_tg} {bot.web_server_host} {bot.web_server_port}")

    # logging.info(f"\n\n  === Добавления бота в Nginx конфигурацию ===\n")
    bot_proc = run_com(activate_bot_scr)
    # logging.info(f"\n{bot_proc.stdout}\n=== Ошибка: ===\n{bot_proc.stderr}")

    # logging.info(f"\n{bot_proc.stdout}\n")
    # if bot_proc.returncode == 1:
    #     logging.info(f"\n=== ERROR: ===\n{bot_proc.stderr}")

    return bot_proc


# ================================================
# ================================================
# ================================================
# # ========= set_token via request =============
#
# def set_token_request(active: bool, token: str) -> User:
#     url = "https://api.telegram.org/bot6189775277%3AAAEdN3J6195JHePhN4wfE-BZTszwFB-MtAQ/setWebhook"
#
#     payload = {
#         # "url": "https://194.58.92.239:8443/bot/6189775277:AAEdN3J6195JHePhN4wfE-BZTszwFB-MtAQional",
#         "url": "https://rupyt.ru:8443/bot/6189775277:AAEdN3J6195JHePhN4wfE-BZTszwFB-MtAQ",
#         "certificate": "",
#         # "WEBHOOK_SECRET": "change_secret_2024"
#         # "certificate": "Optional"
#     }
#     headers = {
#         "accept": "application/json",
#         "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
#         "content-type": "application/json",
#         # "WEBHOOK_SECRET": "change_secret_2024"
#     }
#
#     response = requests.post(url, json=payload, headers=headers)
#
#     print(response.text)
#
# # ========= END set_token via request =============
# ================================================
# # Скрипт формирования self-signed SSL сертификатов:
# ssl_scr = "./Scripts/ssl.sh " + config_Manage.PUBLIC_IP
#
# # Скрипт подготовки предварительной Nginx конфигурации:
# nginx_scr = "./Scripts/nginx.sh " + config_Manage.PUBLIC_IP
# -----------------------
# def prepare_Nginx():
#     """
#      Предварительная подготовка Nginx сервера:
#      1. Подготовка самоподписанных ssl сертификатов
#        Запуск в шелле: ./Scripts/ssl.sh 178.1.1.1
#      2. Предварительная подготовка Nginx конфигурации
#        Запуск в шелле: ./Scripts/nginx_prepare.sh 178.1.1.1
#        Первый параметр в строке запуска $1 - public_ip, внешний IP адрес (пример 178.1.1.1)
#     :return:
#     """
#     logging.info(f"\n\n  === Предварительная подготовка Nginx сервера: ===\n")
#
#     ssl = run_com(ssl_scr)  # Запуск скрипта
#     logging.info(f"\n{ssl.stdout}\n=== SSL: ===\n{ssl.stderr}")
#
#     nginx = run_com(nginx_scr)  # Запуск скрипта
#     logging.info(f"\n{nginx.stdout}\n=== Ошибка: ===\n{nginx.stderr}")
# ========= LOGS =============================
# LOG_FILE = config_Manage.LOG_MANAGE
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.INFO)
#
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s',
#     handlers=[logging.FileHandler(LOG_FILE, mode='a'), stream_handler])  # mode='w'
# ===========================================
# ================================================
# ================================================
# ================================================


