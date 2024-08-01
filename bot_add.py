import asyncio
import logging
import sys
from typing import Union, Dict, Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.session import aiohttp
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.utils.token import validate_token, TokenValidationError

# OTHER_BOTS_URL = f"{BASE_URL}{OTHER_BOTS_PATH}"
# BASE_BOTS_URL = f"https://528d-178-204-213-19.ngrok-free.app/"
BASE_BOTS_URL = f"https://16ea-178-204-13-245.ngrok-free.app/"


def is_bot_token(value: str) -> Union[bool, Dict[str, Any]]:
    try:
        validate_token(value)
    except TokenValidationError:
        return False
    return True


# @main_router.message(Command("add", magic=F.args.func(is_bot_token)))
# async def command_add_bot(message: Message, command: CommandObject, bot: Bot) -> Any:
async def add_bot(token: str) -> Any:
    if not is_bot_token(token):
        return "==Неверный token=="

    session = AiohttpSession()
    try:
        new_bot = Bot(token=token, session=session)
        bot_user = await new_bot.get_me()
    except TelegramUnauthorizedError:
        return "==Invalid token=="

    print("=== Добавление бота ===: ", bot_user)
    await new_bot.delete_webhook(drop_pending_updates=True)
    # await new_bot.set_webhook(BASE_BOTS_URL.format(bot_token=token))
    await new_bot.set_webhook(f"{BASE_BOTS_URL}{token}")
    await new_bot.session.close()

    return f"==Bot @{bot_user.username}: successful added"


async def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    tg_token = input("Введите токен: ")
    result = await add_bot(tg_token)
    print("==Результат==: ", result)


if __name__ == '__main__':
    # main()
    # async session = aiohttp.ClientSession()
    # session = AiohttpSession()
    # use the session here
    asyncio.run(main())
    # session.close()


