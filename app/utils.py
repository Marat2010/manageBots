import asyncio
import logging
import shlex
import subprocess
from typing import Union, Dict, Any

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import (TelegramUnauthorizedError, TelegramBadRequest,
                                TelegramNotFound)
from aiogram.types import FSInputFile, User
from aiogram.utils.token import TokenValidationError, validate_token
from fastapi import HTTPException

from app.models import ActiveBot, BotsOrm
from app.config_manage import config_Manage, BASE_WEBHOOK_URL, WEBHOOK_SSL_CERT

# ========= TG ===============================
SELF_SSL = config_Manage.SELF_SSL
WEBHOOK_PATH = config_Manage.WEBHOOK_PATH
WEBHOOK_SECRET = config_Manage.WEBHOOK_SECRET

# ========= LOGS =============================
LOG_FILE = config_Manage.LOG_MANAGE
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, mode='a'), stream_handler])  # mode='w'
# ===========================================


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
        logging.info(f"\n\n  === Неверный {token= }, Ошибка: '{e}' ===\n")
        raise HTTPException(status_code=422,
                            detail=f"=== Неверный {token= }, Ошибка: '{e}' ===")
    except TokenValidationError as e:
        logging.info(f"\n\n  === Токен не прошел валидацию {token= }, Ошибка: '{e}' ===\n")
        raise HTTPException(status_code=422,
                            detail=f"=== Токен не прошел валидацию {token= }, Ошибка: '{e}' ===")
    except TelegramNotFound as e:
        logging.info(f"\n\n  === Вебхук не установлен {token= }, Ошибка: '{e}' ===\n")
        raise HTTPException(status_code=422,
                            detail=f"=== Вебхук не установлен {token= }, Ошибка: '{e}' ===")
    except Exception as e:
        logging.info(f"\n\n  === Неизвестная ошибка! {token= }, Ошибка: '{e}' ===\n")
        raise HTTPException(status_code=422,
                            detail=f"=== Неизвестная ошибка! {token= }, Ошибка: '{e}' ===")
    await new_bot.delete_webhook(drop_pending_updates=True)

    logging.info(f"\n\n  === Удален вебхук для токена: {token}, пользователь: {bot_info.username} ===\n")
    logging.info(f"\n\n  === {BASE_WEBHOOK_URL=} ===\n")
    logging.info(f"\n\n  === {WEBHOOK_PATH=} ===\n")
    logging.info(f"\n\n  === {WEBHOOK_SSL_CERT=} ===\n")
    logging.info(f"\n\n  === {WEBHOOK_SECRET=} ===\n")

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
            logging.info(f"\n\n  === Возможно недопустимый символ (@,$,&,..)."
                         f" Разрешены только символы A-Z, a-z, 0-9, _и -."
                         f" {WEBHOOK_SECRET= }, Ошибка: '{e}' ===\n")
            raise HTTPException(status_code=422,
                                detail=f"=== Возможно недопустимый символ (@,$,&,..)."
                                       f" Разрешены только символы A-Z, a-z, 0-9, _и -."
                                       f" {WEBHOOK_SECRET= }, Ошибка: '{e}' ===")
        except Exception as e:
            logging.info(f"\n\n  === ! Неизвестная ошибка ! {token= }, Ошибка: '{e}' ===\n")
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
            logging.info(f"\n=== ERROR: ===\n{bot_proc.stderr}")
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
            logging.info(f"\n=== ERROR: ===\n{bot_proc.stderr}")
            raise HTTPException(status_code=422,
                                detail=f"=== Не УДАЛОСЬ удалить бота из конфигурации Nginx !!!\n"
                                       f" Ошибки: '{bot_proc.stderr}' ===")
        logging.info(f"\n{bot_proc.stdout}\n")

        return bot_info


# ============ Nginx =============================

# Скрипт формирования self-signed SSL сертификатов:
ssl_scr = "./Scripts/ssl.sh " + config_Manage.PUBLIC_IP

# Скрипт подготовки предварительной Nginx конфигурации:
nginx_scr = "./Scripts/nginx.sh " + config_Manage.PUBLIC_IP


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


def prepare_Nginx():
    """
     Предварительная подготовка Nginx сервера:
     1. Подготовка самоподписанных ssl сертификатов
       Запуск в шелле: ./Scripts/ssl.sh 178.1.1.1
     2. Предварительная подготовка Nginx конфигурации
       Запуск в шелле: ./Scripts/nginx_prepare.sh 178.1.1.1
       Первый параметр в строке запуска $1 - public_ip, внешний IP адрес (пример 178.1.1.1)
    :return:
    """
    logging.info(f"\n\n  === Предварительная подготовка Nginx сервера: ===\n")

    ssl = run_com(ssl_scr)  # Запуск скрипта
    logging.info(f"\n{ssl.stdout}\n=== SSL: ===\n{ssl.stderr}")

    nginx = run_com(nginx_scr)  # Запуск скрипта
    logging.info(f"\n{nginx.stdout}\n=== Ошибка: ===\n{nginx.stderr}")


def activate_bot_nginx(bot: BotsOrm):
    activate_bot_scr = f"./Scripts/activate_bot_nginx.sh {bot.active.name} {config_Manage.WEBHOOK_PATH} {bot.token_tg} {bot.web_server_host} {bot.web_server_port}"
    # logging.info(f"\n\n  === Добавления бота в Nginx конфигурацию ===\n")
    bot_proc = run_com(activate_bot_scr)
    # logging.info(f"\n{bot_proc.stdout}\n=== Ошибка: ===\n{bot_proc.stderr}")

    # logging.info(f"\n{bot_proc.stdout}\n")
    # if bot_proc.returncode == 1:
    #     logging.info(f"\n=== ERROR: ===\n{bot_proc.stderr}")

    return bot_proc


# def del_bot_nginx(bot: BotsOrm):
#     del_bot_scr = f"./Scripts/del_bot_nginx.sh {config_Manage.WEBHOOK_PATH} {bot.token_tg} {bot.web_server_host} {bot.web_server_port}"
#     logging.info(f"\n\n  === Удаление бота из Nginx конфигурации ===\n")
#     bot_proc = run_com(del_bot_scr)
#     return bot_proc

# =================================================
# =================================================
# =================================================
# add_bot_nginx(token)  # Добавление в конфигурация Nginx бота,
# Лучше сделать это в "ручках" bots.py, после получения всех данных о боте.
# Нужны:
# token_tg, web_server_host, web_server_port, WEBHOOK_PATH, возможно BASE_WEBHOOK_URL
# =================================================
#     ssl = run_com(ssl_scr)  # Запуск скрипта
#     logging.info(f"\n{ssl.stdout}\n")
#
#     if ssl.returncode == 1:
#         logging.info(f"\n=== ERROR ===:\n{ssl.stderr}")
#
#     nginx = run_com(nginx_scr)  # Запуск скрипта
#     logging.info(f"\n{nginx.stdout}\n")
#
#     if ssl.returncode == 1:
#         logging.info(f"\n=== ERROR ===:\n{nginx.stderr}")
# =================================================
    # logging.info(f"\n{ssl.stdout}\n=== ERROR ===:\n{ssl.stderr}")
    # logging.info(f"\n{nginx.stdout}\n=== ERROR ===:\n{nginx.stderr}")
# =================================================
# def run_com(com_line: str) -> subprocess.CompletedProcess[str]:
# # ========= Nginx =============================
# public_ip = config_Manage.PUBLIC_IP
# cmd_create_ssl = (f"openssl req -newkey rsa:2048 -sha256 -nodes -keyout SSL/{public_ip}.self.key"
#                   f" -x509 -days 365 -out SSL/{public_ip}.self.crt"
#                   f" -subj '/C=RU/ST=RT/L=KAZAN/O=Home/CN=$domain_ip'")
#
# cmd_ssl_link = (f"mkdir -p -v /etc/ssl/nginx &&"
#                 f" ln -s SSL/{public_ip}.self.key /etc/ssl/nginx/{public_ip}.self.key"
#                 f" && ln -s SSL/{public_ip}.self.key /etc/ssl/nginx/{public_ip}.self.key")
#
#
# def run_command(command_line) -> str:
#     command_split = shlex.split(command_line)
#
#     print(command_split)
#
#     proc = subprocess.run(
#         command_split,
#         stdout=subprocess.PIPE,
#         encoding="ascii",)
#
#     return proc.stdout
# ====================================
# ====================================
# ====================================
# mkdir -p -v SSL2/A1
# ====================================
    # if proc.returncode != 0:
    #     print("--Ошибкаааа---- ", proc.stderr)
    # else:
    #     print("===OKKKKKKK === ", proc.stdout)
    # ------------------
    # command_line = 'systemctl start docker.service'
    # command_line = 'sudo mkdir /etc/ssl/nginx/'
    # command_line = f'mkdir {dir_name} && touch {dir_name}/{file_name}'
    # command_line = f'touch {dir_name}/{file_name}'
# ====================================
# openssl req -newkey rsa:2048 -sha256 -nodes -keyout $domain_ip.self.key -x509 -days 365 -out $domain_ip.self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Home/CN=$domain_ip"
# ====================================
# BASE_WEBHOOK_URL = BASE_WEBHOOK_URL
# WEBHOOK_SSL_CERT = config_Manage.WEBHOOK_SSL_CERT

# ============================================
# if SELF_SSL:
#     public_ip = requests.get('https://api.ipify.org').text
#     print(f"=== IP Address === {public_ip=}")
#     public_ip = "178.204.228.105"  # убрать в реальном проекте (Сертификат делается заранее)
#     WEBHOOK_SSL_CERT = "/etc/ssl/nginx/" + public_ip + ".self.crt"
#     WEBHOOK_SSL_PRIV = "/etc/ssl/nginx/" + public_ip + ".self.key"
# ====================================
#     if not is_bot_token(token):
#         logging.info(f"\n\n  === Токен не прошел валидацию {token=:} ===\n")
#         return None
# --------------
# def is_bot_token(value: str) -> bool: НЕ работает, всегда выдает "True"
#     try:
#         res = validate_token(value)  # НЕ работает, всегда выдает "True"
#         logging.info(f"\n\n  === Валидация {res=:} ===\n")
#     except TokenValidationError as e:
#         logging.info(f"\n\n  === Токен не прошел валидацию {value=:}, {e} ===\n")
#         return False
#     return True
# ====================================
# def run_set_token(token: Any) -> Any:
#     # run_set = asyncio.run(set_token("6615142110:AAHbuZTgRmqdGibn5MnzRD67CgflJqGJnJQ"))
#     run_set = asyncio.run(set_token(token))
#     if asyncio.run(set_token(token)).get("bot_username"):
#
#
#     return run_set
# ====================================
# def is_bot_token(value: str) -> Union[bool, Dict[str, Any]]:
# ====================================
# ---111111----bot_user-------
# id=6479059814
# is_bot=True
# first_name='auth_bot' last_name=None
# username='VerifyAuthBot'
# language_code=None
# is_premium=None
# added_to_attachment_
# menu=None
# can_join_groups=True
# can_read_all_group_messages=False
# supports_inline_queries=False
# can_connect_to_business=False
# has_main_web_app=False

# ====================================
# BASE_BOTS_URL = config_Manage.BASE_BOTS_URL
# ====================================
#         print("==3_5_1==StateBot.Not_Active==----", state.name)
#         print("==3_5_1==StateBot.Not_Active==----", state.value)
# ====================================