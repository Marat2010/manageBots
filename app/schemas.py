from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from config_manage import config_Manage, BASE_WEBHOOK_URL
# from .models import ActiveBot
from models import ActiveBot


class SBotBase(BaseModel):
    web_server_host: str = Field(default=config_Manage.WEB_SERVER_HOST, min_length=1, max_length=256,
                                 description="IP адрес локально запущенного бота")
    web_server_port: int = Field(..., description="Порт на котором локально запущен бот")
    description: str | None = Field(default="Бот делает ...", min_length=1, max_length=256,
                                    description="Краткое описание функционала бота (что он делает)")
    active: ActiveBot = Field(default=ActiveBot.No, description="Состояние бота: Active, Not_Active, added")
    token_tg: str = Field(..., description="Токен ТГ, к которому привязан функционал бота")
    # base_webhook_url: str = Field(default=config_Manage.BASE_WEBHOOK_URL,
    base_webhook_url: str = Field(default=BASE_WEBHOOK_URL,
                                  description="Веб хук URL, внешний IP c портом 8443")


class SBot(SBotBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bot_username: str = Field(default=None, description="Токен ТГ, к которому привязан функционал бота")
    created_at: datetime
    updated_at: datetime


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


# ================================
# ================================
# class SBotUpdate(SBotBase):
#     id: int
# ================================
    # @model_validator(mode="before")
    # def validate_fields(self, values):
    #     print("====values", values)
    #     if not values.get("id"):
    #         raise ValueError("Either a or b must be provided")
    #     return values  # omitting this line will lead to the error
# ================================
# from datetime import datetime, date
# from typing import Optional
# import re
# ================================
    # enrollment_year: int = Field(..., ge=2002, description="Год поступления должен быть не меньше 2002")
    # major_id: int = Field(..., ge=1, description="ID специальности студента")
    # course: int = Field(..., ge=1, le=5, description="Курс должен быть в диапазоне от 1 до 5")
    # special_notes: Optional[str] = Field(None, max_length=500,
    #                                      description="Дополнительные заметки, не более 500 символов")
    # photo: Optional[str] = Field(None, max_length=100, description="Фото студента")
    # major: Optional[str] = Field(..., description="Название факультета")
    #
    # @field_validator("phone_number")
    # @classmethod
    # def validate_phone_number(cls, values: str) -> str:
    #     if not re.match(r'^\+\d{1,15}$', values):
    #         raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
    #     return values
    #
    # @field_validator("date_of_birth")
    # @classmethod
    # def validate_date_of_birth(cls, values: date):
    #     if values and values >= datetime.now().date():
    #         raise ValueError('Дата рождения должна быть в прошлом')
    #     return values
# ================================
# ================================
