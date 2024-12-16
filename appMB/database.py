import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from appMB.config_m import config_M

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

sync_engine = create_engine(
    config_M.DATABASE_URL_SQLITE,
    echo=False,
    connect_args={'check_same_thread': False},  # Только для SQLite
)

session_factory = sessionmaker(sync_engine)


class Base(DeclarativeBase):
    pass


# ======= Если нет базы данных============================
def create_tables():
    # sync_engine.echo = True
    # Base.metadata.drop_all(sync_engine)  # Для удаления раскомментировать
    sync_engine.echo = False
    Base.metadata.create_all(sync_engine)
    sync_engine.echo = False
    # sync_engine.echo = True


# ====== определяем зависимость для сессий =============
def get_db():  #
    db_session = session_factory()
    try:
        yield db_session
    finally:
        db_session.close()

# ===================================
# ===================================
# sync_engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
# ===================================
