import datetime
import enum
from typing import Annotated, Optional
from sqlalchemy import Table, Column, Integer, String, MetaData, text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from DB.database import Base
from app.database import Base
from app.config_manage import config_Manage, BASE_WEBHOOK_URL

intpk = Annotated[int, mapped_column(primary_key=True)]
str_256 = Annotated[str, 256]

created_at = Annotated[datetime.datetime, mapped_column(
    server_default=func.now())]

updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=func.now(),
        onupdate=datetime.datetime.utcnow
    )]


class ActiveBot(enum.Enum):
    Yes = "Да"
    No = "Нет"


class BotsOrm(Base):
    __tablename__ = "bots"
    # __table_args__ = {'extend_existing': True}

    id: Mapped[intpk]
    web_server_host: Mapped[str_256] = mapped_column(nullable=False)
    web_server_port: Mapped[int] = mapped_column(nullable=False, unique=True)
    description: Mapped[str_256 | None]
    active: Mapped[ActiveBot] = mapped_column(default="No")
    token_tg: Mapped[str_256] = mapped_column(nullable=False, unique=True)
    bot_username: Mapped[str_256] = mapped_column(nullable=True)
    base_webhook_url: Mapped[str_256] = mapped_column(default=BASE_WEBHOOK_URL)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"web_server_host={self.web_server_host!r},"
                f"web_server_port={self.web_server_port!r},"
                f"description={self.description!r},"
                f"active={self.active!r},"
                f"token_tg={self.token_tg!r}),"
                f" bot_username={self.bot_username!r},"
                f" base_webhook_url={self.base_webhook_url!r},"
                )

    def __repr__(self):
        return str(self)

# =========================================
# =========================================
    # base_webhook_url: Mapped[str_256] = mapped_column(default=config_Manage.BASE_WEBHOOK_URL)
# =========================================
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../")))
# print("====0000-----", os.path.dirname(os.path.abspath(__file__)))
# print("====0001-----", os.path.dirname(os.path.abspath(__file__ + "/../")))
#
# from config_manage import config
# =========================================
# sys.path.insert(1, os.path.join(sys.path[0], '..'))
# =========================================
# created_at = Annotated[datetime, mapped_column(
    # server_default=datetime.now(timezone.utc))]

    # server_default=text("DATETIME()"))]
    # server_default=text("datetime.datetime.now(tz=datetime.timezone.utc)"))]
    # server_default=text("datetime.datetime.utcnow"))]

    # created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    # updated_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


# tz = datetime.datetime("TIMEZONE('utc', now())")
# print(f"{tz=}")
# tz1 = datetime.datetime.now(tz=datetime.timezone.utc)
# tz1 = datetime.datetime.utcnow()
# print(f"{tz1=}")

