"""
This example shows how to use webhook on behind of any reverse proxy (nginx, traefik, ingress etc.)

Пример взят https://docs.aiogram.dev/en/latest/dispatcher/webhook.html
Немного изменён способ получения переменных окружения через config.
"""

import logging
import sys
from os import getenv

from aiohttp import web

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.utils.markdown import hbold
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# ======= Добавлено ==========================
import ssl
from config_bots import config_bot, WEBHOOK_SSL_CERT, WEBHOOK_SSL_KEY
# ------------------------------

# ========= TG ===============================
SELF_SSL = config_bot.SELF_SSL  # Для случаев, когда нет нормального сертификата на домен
WEBHOOK_PATH_BASE = config_bot.WEBHOOK_PATH_BASE
# ============================================

# Bot token can be obtained via https://t.me/BotFather
# TOKEN = getenv("BOT_TOKEN")
# TOKEN_TG = config_bot.TOKEN_TG.get_secret_value()  # Получение через config
TOKEN_TG = config_bot.TOKEN_TG  # Получение через config

# Webserver settings
# bind localhost only to prevent any external access
# WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_HOST = config_bot.WEB_SERVER_HOST  # Получение через config

# Port for incoming request from reverse proxy. Should be any available port
# WEB_SERVER_PORT = 8080
WEB_SERVER_PORT = config_bot.WEB_SERVER_PORT

# Path to webhook route, on which Telegram will send requests
# WEBHOOK_PATH = "/webhook"
WEBHOOK_PATH = f"{WEBHOOK_PATH_BASE}{TOKEN_TG}"  # Токен в качестве пути

# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public DNS with HTTPS support
# BASE_WEBHOOK_URL = "https://aiogram.dev"
BASE_WEBHOOK_URL = config_bot.BASE_WEBHOOK_URL  # Получение через config

# Secret key to validate requests from Telegram (optional)
WEBHOOK_SECRET = config_bot.WEBHOOK_SECRET

# All handlers should be attached to the Router (or Dispatcher)
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}! I'm a first bot!")


@router.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.answer(f"Это Первый Бот. Он проверяет оплату ...) "
                             f"Локально запущен: {WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    # ======= Добавлено ==========================
    if SELF_SSL:
        await bot.set_webhook(
            f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
            certificate=FSInputFile(WEBHOOK_SSL_CERT),
            secret_token=WEBHOOK_SECRET,
        )
    else:
        await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)
    # ===============================================


# === (Added) Register shutdown hook to initialize webhook ===
async def on_shutdown(bot: Bot) -> None:
    """
    Graceful shutdown. This method is recommended by aiohttp docs.
    """
    # Remove webhook.
    await bot.delete_webhook()


def main() -> None:
    # Dispatcher is a root router
    dp = Dispatcher()
    # ... and all other routers should be attached to Dispatcher
    dp.include_router(router)

    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN_TG, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # ======= Добавлено ==========================
    if SELF_SSL:  # ==== For self-signed certificate ====
        # Generate SSL context
        # context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)  # устарел
        context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_KEY)

        # And finally start webserver
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, ssl_context=context)
    else:
        # And finally start webserver
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    # =============================================


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # LOG_FILE = config_bot.LOG_MANAGE
    # stream_handler = logging.StreamHandler()
    # stream_handler.setLevel(logging.INFO)
    #
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s',
    #                     handlers=[logging.FileHandler(LOG_FILE, mode='a'), stream_handler],
    #                     stream=sys.stdout)
    main()


# ===========================================================
# ===========================================================
# WEBHOOK_SECRET = config_bot.WEBHOOK_SECRET

# if SELF_SSL:
#     public_ip = requests.get('https://api.ipify.org').text
#     print("=== IP Address ===", public_ip)
#     public_ip = "178.204.228.105"  # убрать в реальном проекте
#     WEBHOOK_SSL_CERT = "/etc/ssl/nginx/" + public_ip + ".self.crt"
#     WEBHOOK_SSL_PRIV = "/etc/ssl/nginx/" + public_ip + ".self.key"
# ===========================================================