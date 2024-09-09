import logging
import os
import sqlite3

import requests
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # ======= DB =======
    DATABASE_URL_SQLITE: str = "./mb.sqlite3"

    # === Telegram settings for bots ===
    SELF_SSL: bool = True  # Для случаев, когда нет нормального сертификата на домен или IP
    PUBLIC_IP: str | None = None  # Внешний IP адрес
    WEBHOOK_PATH_BASE: str = "/bot/"  # Часть полного пути вебхук урла (BASE_WEBHOOK_URL + WEBHOOK_PATH + токен)
    WEBHOOK_SECRET: str = "secret_2024"  # Безопасность (входящие запросы исходят от ТГ сервера).

    # === Telegram settings (WEB SERVER) ===
    # Желательно вместо str использовать SecretStr для конфиденциальных данных, например, токена бота
    # TOKEN_TG: SecretStr = "**********"
    TOKEN_TG: str = "6615***:AAHb***"

    WEB_SERVER_HOST: str = "127.0.0.1"  # Если нет данных в ".env", то берется по умолчанию "127.0.0.1"
    WEB_SERVER_PORT: int        # Установите в ".env_bot" номер свободного порта из диапозона 15001-65535
    BASE_WEBHOOK_URL: str = "https://178.1.1.1:8443"

    model_config = SettingsConfigDict(env_file=f'./our_Bots/bot_SetPort/.env_bot', env_file_encoding='utf-8', extra='ignore')
    # Начиная со второй версии pydantic, настройки класса настроек задаются через model_config
    # В данном случае будет использоваться файла .env, который будет прочитан с кодировкой UTF-8
    # Пример пути файла на 2 уровня вверх: env_file='../../.env', или в "utils": env_file='utils/.env'
    # ДАННЫЕ БЕРУТСЯ СНАЧАЛА из переменных окружения в системе, если их там нет, то из файла ".env",
    # если и там нет, то значения по умолчанию отсюда


# При импорте файла сразу создастся и провалидируется объект конфига, который можно импортировать из разных мест
config_bot = Settings()

if not config_bot.PUBLIC_IP:  # Если неуказан внешний IP адрес или домен
    config_bot.PUBLIC_IP = requests.get('https://api.ipify.org').text

# Формирование BASE_WEBHOOK_URL и путей для серификатов SSL
config_bot.BASE_WEBHOOK_URL = f"https://{config_bot.PUBLIC_IP}:8443"
WEBHOOK_SSL_CERT = "/etc/ssl/nginx/" + config_bot.PUBLIC_IP + ".self.crt"
WEBHOOK_SSL_KEY = "/etc/ssl/nginx/" + config_bot.PUBLIC_IP + ".self.key"

# ========= LOGS =============================
LOG_FILE = f"./our_Bots/bot_{config_bot.WEB_SERVER_PORT}/bot_{config_bot.WEB_SERVER_PORT}.log"
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(module)s] [%(funcName)s]: %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, mode='a'), stream_handler])  # mode='w'

# ============= DB ===========================
conn = sqlite3.connect(config_bot.DATABASE_URL_SQLITE)


def get_from_DB(web_server_port: int) -> tuple | None:
    """
    Получение данных о боте, если он занесен в Базу данных и уже
    управляется менеджером.
    Привязка функционала бота идет по web_server_port
    :param web_server_port: Порт, начиная с 15001 (уникален, для каждого бота)
    :return: bot_db: Данные бота с Базы данных
    """
    try:
        with conn:
            cur = conn.cursor()
            bot_db = cur.execute('SELECT * FROM bots WHERE web_server_port=?', (web_server_port,)).fetchone()
    except sqlite3.Error as e:
        logging.error(f"=== Ошибка: {e= } ====\n")
        return None
    return bot_db


bot = get_from_DB(config_bot.WEB_SERVER_PORT)  # Получение данных с БД
logging.info(f"=== Получение данных с БД: ===\n{bot}\n")

if bot:  # Если бот в БД, то настройки берутся оттуда, иначе с ".env_bot"
    config_bot.WEB_SERVER_HOST = bot[1]
    config_bot.TOKEN_TG = bot[5]
    config_bot.BASE_WEBHOOK_URL = bot[7]

# ========= Вывод конечных настроек ============================
logging.info(f"=== Настройки: ===")
logging.info(f"{WEBHOOK_SSL_CERT= }")
logging.info(f"{WEBHOOK_SSL_KEY= }")
logging.info(f"{LOG_FILE= }")
[logging.info(f"{param}") for param in config_bot]


# ==============================================================
# ==============================================================
# ==============================================================
# model_config = SettingsConfigDict(env_file='./our_Bots/bot_15001/.env_bot', env_file_encoding='utf-8', extra='ignore')
# model_config = SettingsConfigDict(env_file=f'.env_bot', env_file_encoding='utf-8', extra='ignore')
# ==============================================================
# port = os.environ.get("WEB_SERVER_PORT")
# load_dotenv('/home/miguel/my_project/.env')
# ==============================================================
# LOG_FILE = config_bot.LOG_Bot_File
# LOG_FILE = f"./our_Bots/bot_15001/logs/bot.log"
# ==============================================================
# logging.info(f"=== Настройки для бота: ===\n")
# for i in config_bot:
#     logging.info(f"{i}")
# ==============================================================
# cursor = conn.cursor()
# logging.info(config_bot.TOKEN_TG.get_secret_value())
# ==============================================================
# print("DATABASE_URL_SQLITE:=======", config_bot.DATABASE_URL_SQLITE)
# print("WEB_SERVER_PORT:=======", config_bot.WEB_SERVER_PORT)
# ==============================================================
# DATABASE_URL_SQLITE: str = "sqlite+pysqlite:///./DB/mb.sqlite3"
# ==============================================================
# ==============================================================
    # data = data_to_dataDB(data_dict)  # Переводим словарь данных в кортеж, для последующего занесения в БД

    # try:
    #     cursor.execute("INSERT INTO payments (date,order_id,order_num,sum,customer_phone,customer_email,"
    #                "products_name,payment_init) VALUES (?,?,?,?,?,?,?,?)", data)
    #     # logging.info(f"=== Данные внесены. Файл БД Sqlite: {os.path.abspath(DB_SQLITE_NAME)} ===")
    #
    # except OperationalError as e:
    #     # logging.warning(f" =! Нет Файла БД Sqlite !=: {e}")
    #     # logging.warning(f"=! Данные НЕ внесены.!!! Создаем БД !=\n")
    #     # create_DB()
    #     # logging.info(f"=== Создан Файл БД Sqlite: {os.path.abspath(DB_SQLITE_NAME)} ===")
    #     # logging.info("=== Повторяем последнюю операцию!!! ===\n")
    #     add_payments(data)
    #
    # except ProgrammingError as e:
    #     logging.error(f"=!!! Неверное количество предоставленных данных !!!=: {e}")
    #
    # except Exception as e:
    #     logging.error(f" =!!! Ошибка !!!=: {e}")

# ==============================================================
    # model_config = SettingsConfigDict(env_file='.env_bot', env_file_encoding='utf-8', extra='ignore')
    # model_config = SettingsConfigDict(env_file='.env_bot', env_file_encoding='utf-8', extra='ignore')
    # model_config = SettingsConfigDict(env_file='bot1/.env', env_file_encoding='utf-8', extra='ignore')

# ==============================================================
# con = sqlite3.connect(f"./{config_bot.DATABASE_URL_SQLITE}")
# conn = sqlite3.connect("./our_Bots/bot1/mb.sqlite3")
# bot = cur.execute('SELECT * FROM bots').fetchone()
# bot = cur.execute('SELECT * FROM bots WHRERE web_server_port=?', (web_server_port,)).fetchone()
# # cursor.execute('select * from mb where WEB_SERVER_PORT=?', (WEB_SERVER_PORT,))
# cursor.execute('select * from bots where WEB_SERVER_PORT=?', (WEB_SERVER_PORT,))
# # cursor.execute('select * from bots')
# rows = cursor.fetchall()
# print("===rows ====    ", rows)
# conn.commit()
# bot = cur.execute('SELECT * FROM bots')
#     # with sqlite3.connect(database) as conn:
#     with conn as con:
#         rows = cur.fetchall()
#         for row in rows:
#             print("---- Строки ---- ", row)
# ==============================================================
# print("=== Настройки: ===")  # Можно после закоментировать
# [print(i) for i in config]

