from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from appMB.config_m import config_M, BASE_WEBHOOK_URL
# from .models import ActiveBot
from appMB.models import ActiveBot, BaseWebhookUrlOrm


class SUrlBase(BaseModel):
    url: str = Field(default=BASE_WEBHOOK_URL,
                     description="Веб хук URL, внешний IP c портом 8443")


class SUrl(SUrlBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SUrlAdd(SUrlBase):
    pass


class SBotBase(BaseModel):
    web_server_host: str = Field(default=config_M.WEB_SERVER_HOST, min_length=1, max_length=256,
                                 description="IP адрес локально запущенного бота")
    web_server_port: int = Field(..., description="Порт на котором локально запущен бот")
    description: str | None = Field(default="Бот делает ...", min_length=1, max_length=256,
                                    description="Краткое описание функционала бота (что он делает)")
    active: ActiveBot = Field(default=ActiveBot.No, description="Состояние бота: Active, Not_Active, added")
    token_tg: str = Field(..., description="Токен ТГ, к которому привязан функционал бота")
    url_bwh_id: int = Field(default=1, foreign_key="base_webhook_url.id")


class SBot(SBotBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bot_username: str = Field(default=None, description="Пользователь ТГ")
    created_at: datetime
    updated_at: datetime


class SBotAddOwner(BaseModel):
    token_tg: str = Field(..., description="Токен ТГ, к которому привязан функционал бота")


class SBotAdd(SBotBase):
    pass


class SBotUpd(SBotBase):  # Общее редактирование бота по 'id'
    token_tg: str = Field(description="Токен ТГ, к которому привязан функционал бота")


class SBotDel(SBot):
    model_config = ConfigDict(from_attributes=True)
    deleted: bool


# =======================================================
# ============== For Manage bots ========================
# ============ by web_server_port =======================
class SBotGetByPort(BaseModel):
    web_server_port: int = Field(..., description="Порт на котором локально запущен бот")


class SBotUpdateByPort(SBotGetByPort):
    active: ActiveBot = Field(default=ActiveBot.No, description="Состояние бота: Active, Not_Active, added")


# =======================================================
# ============== For Manage bots ========================
# ================ by token_tg ==========================
class SBotGetByToken(BaseModel):
    token_tg: str = Field(..., description="Токен ТГ, к которому привязан функционал бота")


class SBotUpdateByToken(SBotGetByToken):
    active: ActiveBot = Field(default=ActiveBot.No, description="Состояние бота: Active, Not_Active, added")


# =======================================================
# ============== Разное =================================
class SBotGetByPortToken(BaseModel):
    web_server_port: int = Field(description="Порт на котором локально запущен бот")
    token_tg: str = Field(description="Токен ТГ, к которому привязан функционал бота")


# ========================================================
# ========================================================
# ========================================================

