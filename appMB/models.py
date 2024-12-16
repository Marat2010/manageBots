import datetime
import enum
from typing import Annotated, List

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from appMB.database import Base, get_db

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


class OwnerOrm(Base):
    __tablename__ = 'owner'
    __table_args__ = {'extend_existing': True}

    id: Mapped[intpk]
    name:  Mapped[str_256]
    email: Mapped[str_256]

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"name={self.name!r},"
                f"email={self.email!r},"
                )

    def __repr__(self):
        return str(self)


class BotsOrm(Base):  # Многие к одному
    __tablename__ = "bots"
    __table_args__ = {'extend_existing': True}

    id: Mapped[intpk]
    web_server_host: Mapped[str_256] = mapped_column(nullable=False)
    web_server_port: Mapped[int] = mapped_column(nullable=False, unique=True)
    description: Mapped[str_256 | None]
    active: Mapped[ActiveBot] = mapped_column(default="No")
    token_tg: Mapped[str_256] = mapped_column(nullable=False, unique=True)
    bot_username: Mapped[str_256] = mapped_column(nullable=True)
    url_bwh_id: Mapped[int] = mapped_column(ForeignKey("base_webhook_url.id"))
    url_bwh: Mapped["BaseWebhookUrlOrm"] = relationship(back_populates="bots")

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
                # f" base_webhook_url={self.base_webhook_url!r},"
                )

    def __repr__(self):
        return str(self)

    @classmethod
    def by_port_get(cls, port: int):
        generator = get_db()
        db_session = next(generator)

        bot = db_session.query(cls).filter(cls.web_server_port == port).first()
        return bot


class BaseWebhookUrlOrm(Base):  # Одна запись для многих ботов
    __tablename__ = 'base_webhook_url'
    __table_args__ = {'extend_existing': True}

    id: Mapped[intpk]
    url: Mapped[str_256] = mapped_column(nullable=False, unique=True)
    bots: Mapped[List["BotsOrm"]] = relationship(back_populates="url_bwh")

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"url={self.url!r},"
                )

    def __repr__(self):
        return str(self)


# ================================================================
# ================================================================

