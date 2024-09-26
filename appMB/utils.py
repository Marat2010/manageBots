import asyncio
import logging
import os
import shlex
import subprocess

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import (TelegramUnauthorizedError, TelegramBadRequest,
                                TelegramNotFound)
from aiogram.types import FSInputFile, User
from aiogram.utils.token import TokenValidationError
from fastapi import HTTPException

from appMB.models import ActiveBot, BotsOrm
from appMB.config_m import config_M, BASE_WEBHOOK_URL, WEBHOOK_SSL_CERT


# ========= TG ===============================
SELF_SSL = config_M.SELF_SSL
WEBHOOK_PATH = config_M.WEBHOOK_PATH
WEBHOOK_SECRET = config_M.WEBHOOK_SECRET


# ========= Local Server Bot ===============================
class ServerPort:
    web_server_port = config_M.START_WEB_SERVER_PORT

    @classmethod
    def set_web_server_port(cls, web_server_port):
        cls.web_server_port = web_server_port
        logging.debug(f"====={cls.web_server_port=} =======")

    @classmethod
    def get_web_server_port(cls) -> int | None:
        """
        Увеличение счетчика порта
        :return: новый "веб сервер порт" для бота
        """

        web_server_port = cls.web_server_port

        while True:
            web_server_port += 1
            logging.debug(f"=== {web_server_port=} ===")

            # Проверка на то, что порт не занят другим ботом (проверка в БД).
            if BotsOrm.by_port_get(web_server_port) is not None:
                logging.debug(f"=========== в БД такой порта есть: {web_server_port}  =========")
                continue

            # ----------------------------------------

            # Проверка на то, что нет такого каталога
            if os.path.exists(f"./our_Bots/bot_{web_server_port}"):
                continue

            # ----------------------------------------

            # Проверка на то, что порт не занят в ОС (ss -nultp |grep порт)
            check_port = f"./Scripts/check_port.sh {web_server_port}"
            proc = run_com(check_port)

            if proc.returncode == 1:  # выход, при условии, что порт не занят
                break
            else:
                logging.debug(f"=========== в ОС такой порт занят: {web_server_port}  =========")

            # ----------------------------------------
        logging.debug(f"=== {web_server_port=} ===")
        return web_server_port


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

    logging.info(f"\n\n  === Удален вебхук для ТГ пользователя '{bot_info.username}': ===\n")
    logging.info(f"\n  === {BASE_WEBHOOK_URL}{WEBHOOK_PATH}{token}, ===\n")

    if active:
        try:
            if SELF_SSL:
                await new_bot.set_webhook(
                    f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}{token}",
                    certificate=FSInputFile(WEBHOOK_SSL_CERT),
                    secret_token=WEBHOOK_SECRET)

                logging.debug(f"\n\n  === new_bot.get_webhook_info(): ===\n{await new_bot.get_webhook_info()}\n")
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


# ============ Nginx =============================
def change_state_bot(bot: BotsOrm, add_del: str = None) -> User:
    """
    Активация или деактивация бота.
    При активации для локально запушенного бота (функционала бота),
     устанавливаем webhook, при остановке удаляем webhook.
    """
    logging.info(f"\n\n  === Состояние бота: ===\n{bot.active=} \n")
    logging.info(f"\n\n  === Модель Бота: ===\n{bot}\n")

    # === 1. Установка или Удаление вебхука ===
    # === в зависимости от bot.active (ActiveBot.Yes или ActiveBot.No) ===

    if bot.active == ActiveBot.Yes:  # === Установка вебхука ===
        bot_info = asyncio.run(set_token(True, bot.token_tg))

    else:  # === Удаление вебхука (bot.active == ActiveBot.No) ===
        bot_info = asyncio.run(set_token(False, bot.token_tg))

    # === 2. Добавление или Удаление бота в файловую систему ===
    # === в зависимости от bot.active (ActiveBot.Yes или ActiveBot.No) ===
    if add_del:  # запуск скрипта только при добавлении или удалени бота
        add_bot_scr = (f"./Scripts/add_bot_FS.sh {bot.active.name} {config_M.WEBHOOK_PATH}"
                       f" {bot.token_tg} {bot.web_server_host} {bot.web_server_port}")
        bot_proc = run_com(add_bot_scr)

        if bot_proc.returncode == 1:  # В случае ошибки при выполнении bash скрипта
            logging.error(f"\n=== ERROR: ===\n{bot_proc.stderr}")
            raise HTTPException(status_code=422,
                                detail=f"=== Не УДАЛОСЬ добавить или удалить бота в, из Файловой системы !!!\n"
                                       f" Ошибки: '{bot_proc.stderr}' ===")
        logging.debug(f"\n=== {bot_proc.stdout=} ===\n")

    # === 3. Добавление или Удаление бота из конфигурации Nginx ===
    # === в зависимости от bot.active (ActiveBot.Yes или ActiveBot.No) ===

    activate_bot_scr = (f"./Scripts/activate_bot_nginx.sh {bot.active.name} {config_M.WEBHOOK_PATH}"
                        f" {bot.token_tg} {bot.web_server_host} {bot.web_server_port}")
    bot_proc = run_com(activate_bot_scr)

    if bot_proc.returncode == 1:  # В случае ошибки при выполнении bash скрипта
        logging.error(f"\n=== ERROR: ===\n{bot_proc.stderr}")
        raise HTTPException(status_code=422,
                            detail=f"=== Не УДАЛОСЬ добавить или удалить бота из конфигурации Nginx !!!\n"
                                   f" Ошибки: '{bot_proc.stderr}' ===")
    logging.debug(f"\n=== {bot_proc.stdout} ===\n")

    return bot_info


def run_com(com_line: str):
    """
    Запуск shell скриптов
    :param com_line: Командная строка для запуска shell скрипта
    :return:
    """
    command_split = shlex.split(com_line)
    logging.info(f"\n  === Командная строка (split): === {command_split}\n")

    proc = subprocess.run(
        command_split,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",)
    return proc


# ================================================
# ================================================

