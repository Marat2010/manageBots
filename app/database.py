import pydantic
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
import sys

from app.config_manage import config_Manage  # for fastapi

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

sync_engine = create_engine(
    config_Manage.DATABASE_URL_SQLITE,
    echo=True,
    connect_args={'check_same_thread': False},
)

session_factory = sessionmaker(sync_engine)


class Base(DeclarativeBase):
    pass


# ======= Если нет базы данных============================
def create_tables():
    sync_engine.echo = False
    # Base.metadata.drop_all(sync_engine)  # Для удаления раскомментировать
    Base.metadata.create_all(sync_engine)
    # sync_engine.echo = True


# ===================================
# ===================================
# ===================================
# sync_engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
# ===================================
# with engine.connect() as conn:
#     res = conn.execute(text("SELECT 1"))


