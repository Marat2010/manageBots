import logging
import sys
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import exc

from ..database import session_factory
# from app.main import logger
from ..models import BotsOrm, ActiveBot
from ..schemas import (SBotBase, SBot, SBotAdd, SBotGetByPort, SBotUpdateByPort,
                       SBotGetByToken, SBotUpdateByToken, SBotDel, SBotUpd)
from ..utils import change_state_bot

router = APIRouter(prefix="/api/bots")


# определяем зависимость
def get_db():  #
    db_session = session_factory()
    try:
        yield db_session
    finally:
        db_session.close()


@router.get("", summary="Получить всех ботов", tags=["Standard"])
def get_bots(db_session: Session = Depends(get_db)) -> List[SBot]:
    bots_models = db_session.query(BotsOrm).all()
    bots = [SBot.model_validate(bot_model) for bot_model in bots_models]
    return bots


@router.get("/{idpk}", summary="Получить бота по 'id'", tags=["Standard"])
def get_by_id(idpk, db_session: Session = Depends(get_db)) -> SBot:
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.id == idpk).first()
    if bot_model is None:
        logging.warning(f"\n\n  === Бот не найден {idpk= } ===\n")
        raise HTTPException(status_code=404, detail="Бот не найден")
    bot = SBot.model_validate(bot_model)
    return bot


# def update_by_id(idpk, bot: SBotBase = Depends(),
@router.put("/update", tags=["Standard"], summary="Общее редактирование бота по 'id'")
def update_by_id(idpk, bot: SBotUpd = Depends(),
                 db_session: Session = Depends(get_db)) -> SBot | dict:
    data = bot.model_dump()
    try:
        db_session.query(BotsOrm).filter(BotsOrm.id == idpk).update(data)
    # except exc.SQLAlchemyError as e:
    except exc.IntegrityError as e:
        logging.error(f"\n\n  === Не верные данные: ===\n{e.args=:}\n")
        db_session.rollback()
        raise HTTPException(status_code=422, detail=f"Не верные данные: {e.args}")

    bot_model = db_session.query(BotsOrm).filter(BotsOrm.id == idpk).first()
    print("-------+++++++ bot_model  ++++++------- ", bot_model)
    return upd_bot(bot_model, data, db_session)


@router.delete("/del/{idpk}", summary="Удалить бота по 'id'", tags=["Standard"])
def delete_by_id(idpk, db_session: Session = Depends(get_db)) -> SBotDel:
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.id == idpk).first()
    return del_bot(bot_model, db_session)


# =======================================================
# ============== For Manage bots ========================
# =======================================================

@router.post("/add", summary="Добавить нового бота", tags=["Manage Bots"])
def add_bot(bot: SBotAdd = Depends(), db_session: Session = Depends(get_db)) -> SBot:
    data = bot.model_dump()
    new_bot_model = BotsOrm(**data)
    db_session.add(new_bot_model)

    logging.info(f"\n\n  === Добавление бота: ===\n{new_bot_model=} \n")
    bot_info = change_state_bot(new_bot_model)  # Отключение или включение вебхука для бота
    new_bot_model.bot_username = bot_info.username

    try:
        db_session.flush()
        db_session.commit()
    except exc.IntegrityError as e:
        logging.error(f"\n\n  === Не верные данные: ===\n{e.args=:}\n")
        db_session.rollback()
        raise HTTPException(status_code=422, detail=f"Не верные данные: {e.args}")

    new_bot = SBot.model_validate(new_bot_model)
    return new_bot


# =======================================================
# ============== For Manage bots ========================
# ============ by web_server_port =======================

@router.post("/get_by_port", tags=["Manage Bots by web_server_port"],
             summary="Получить одного бота по фильтру 'web_server_port'")
def get_by_port(bot: SBotGetByPort = Depends(),
                db_session: Session = Depends(get_db)) -> SBot | dict:
    data = bot.model_dump()
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.web_server_port == data['web_server_port']).first()
    if bot_model is None:
        logging.warning(f"\n\n  === Бот не найден {data['web_server_port']= } ===\n")
        raise HTTPException(status_code=404, detail="Бот не найден")
    bot = SBot.model_validate(bot_model)
    return bot


@router.patch("/update_active_by_port", tags=["Manage Bots by web_server_port"],
              summary="Изменение статуса бота (включить, выключить) по фильтру 'web_server_port'")
def update_by_port(bot: SBotUpdateByPort = Depends(),
                   db_session: Session = Depends(get_db)) -> SBot | dict:
    data = bot.model_dump()
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.web_server_port == data['web_server_port']).first()
    return upd_bot(bot_model, data, db_session)


@router.delete("/del_by_port", summary="Удалить бота по 'web_server_port'", tags=["Manage Bots by web_server_port"])
def delete_by_port(web_server_port, db_session: Session = Depends(get_db)) -> SBotDel:
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.web_server_port == web_server_port).first()
    return del_bot(bot_model, db_session)


# =======================================================
# ============== For Manage bots ========================
# ================ by token_tg ==========================

@router.post("/get_by_token", tags=["Manage Bots by token_tg"],
             summary="Получить одного бота по фильтру 'token_tg'")
def get_by_token(bot: SBotGetByToken = Depends(),
                 db_session: Session = Depends(get_db)) -> SBot | dict:
    data = bot.model_dump()
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.token_tg == data['token_tg']).first()
    if bot_model is None:
        logging.warning(f"\n\n  === Бот не найден {data['token_tg']= } ===\n")
        raise HTTPException(status_code=404, detail="Бот не найден")
    bot = SBot.model_validate(bot_model)
    return bot


@router.patch("/update_active_by_token", tags=["Manage Bots by token_tg"],
              summary="Изменение статуса бота (включить, выключить) по фильтру 'token_tg'")
def update_by_token(bot: SBotUpdateByToken = Depends(),
                    db_session: Session = Depends(get_db)) -> SBot | dict:
    data = bot.model_dump()
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.token_tg == data['token_tg']).first()
    return upd_bot(bot_model, data, db_session)


@router.delete("/del_by_token", summary="Удалить бота по 'token_tg'", tags=["Manage Bots by token_tg"])
def delete_by_token(token_tg, db_session: Session = Depends(get_db)) -> SBotDel:
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.token_tg == token_tg).first()
    return del_bot(bot_model, db_session)


# ================================================
# ============== Общее в методах =================
# ================================================
def upd_bot(bot_model: BotsOrm, data: dict, db_session: Session = Depends(get_db)) -> SBot | dict:
    if bot_model is None:
        logging.warning(f"\n\n  === Бот не найден ===\n")
        raise HTTPException(status_code=404, detail="Бот не найден")

    bot_model.active = data['active']
    bot_info = change_state_bot(bot_model)  # Активация или деактивация бота.
    bot_model.bot_username = bot_info.username

    try:
        db_session.flush()
        db_session.commit()
    except exc.IntegrityError as e:
        db_session.rollback()
        logging.error(f"\n\n  === Не верные данные: ===\n{e.args=:}\n")
        raise HTTPException(status_code=422, detail=f"Не верные данные: {e.args}")
    bot = SBot.model_validate(bot_model)
    return bot  # Можно сразу 'SBot.model_validate(bot_model)'


def del_bot(bot_model: BotsOrm, db_session: Session = Depends(get_db)) -> SBotDel:
    if bot_model is None:
        logging.warning(f"\n\n  === Бот не найден ===\n")
        raise HTTPException(status_code=404, detail="Бот не найден")

    bot_model.active = ActiveBot.No  # Необходимо, чтобы отключить вебхук
    bot_info = change_state_bot(bot_model)  # Отключение бота от вебхука
    bot_model.bot_username = bot_info.username  # МОЖНО УБРАТЬ

    db_session.delete(bot_model)
    db_session.commit()
    bot_model.deleted = True  # Выставляем, чтобы в ответе было видно, что удален.
    bot = SBotDel.model_validate(bot_model)
    return bot  # Можно сразу 'SBot.model_validate(bot_model)'


# ================================================
# ================================================
# ================================================

# # ========== FastAPI Logs================
# logger = logging.getLogger(__name__)
# # logger = logging.getLogger("app.config_manage.logging")
# logger.setLevel(logging.DEBUG)
# stream_handler = logging.StreamHandler(sys.stdout)
# log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
# stream_handler.setFormatter(log_formatter)
# logger.addHandler(stream_handler)
#
# logger.info('API is starting up')
#
# print("+++++++++++++++++++++= ", logger)
# # ========================================
# ================================================
    # # =========----------
    # if bot_model is None:
    #     raise HTTPException(status_code=404, detail="Бот не найден")
    #
    # change_state_bot(bot_model)  # Отключение или включение вебхука для бота
    #
    # db_session.commit()
    # bot = SBot.model_validate(bot_model)
    # return bot
    # # =========----------
# ================================================
    # if upd_bot_model is None:
    #     raise HTTPException(status_code=404, detail="Бот не найден")
    #
    # upd_bot_model.active = data['active']
    # bot_info = change_state_bot(upd_bot_model)  # Отключение или включение вебхука для бота
    # upd_bot_model.bot_username = bot_info.username
    #
    # try:
    #     db_session.flush()
    #     db_session.commit()
    # except exc.IntegrityError as e:
    #     logging.info(f"\n\n  === Не верные данные: ===\n{e.args=:}\n")
    #     db_session.rollback()
    #     raise HTTPException(status_code=422, detail=f"Не верные данные: {e.args}")
    #
    # upd_bot = SBot.model_validate(upd_bot_model)
    # return upd_bot
# -----------------------------------
    # if upd_bot_model is None:
    #     raise HTTPException(status_code=404, detail="Бот не найден")
    #
    # upd_bot_model.active = data['active']
    # bot_info = change_state_bot(upd_bot_model)  # Активация или деактивация бота.
    # upd_bot_model.bot_username = bot_info.username
    #
    # try:
    #     db_session.flush()
    #     db_session.commit()
    #     upd_bot = SBot.model_validate(upd_bot_model)
    # except exc.IntegrityError as e:
    #     logging.info(f"\n\n  === Не верные данные: ===\n{e.args=:}\n")
    #     db_session.rollback()
    #     raise HTTPException(status_code=422, detail=f"Не верные данные: {e.args}")
    #
    # return upd_bot
# ================================================
    # if bot_model is None:
    #     raise HTTPException(status_code=404, detail="Бот не найден")
    #
    # bot_model.active = ActiveBot.No
    # bot_info = change_state_bot(bot_model)  # Отключение бота от вебхука
    # bot_model.bot_username = bot_info.username
    #
    # db_session.delete(bot_model)
    # db_session.commit()
    # bot_model.deleted = True
    # bot = SBotDel.model_validate(bot_model)
    # return bot
# ================================================
    # try:
    #     new_bot_model.bot_username = bot_info.username
    # except AttributeError as e:
    #     raise HTTPException(status_code=422,
    #                         detail=f"=== Неверный токен {new_bot_model.token_tg= :}, Ошибка: {bot_info} ===")

# ================================================
    # try:
    #     upd_bot_model.bot_username = bot_info.username
    # except AttributeError as e:
    #     raise HTTPException(status_code=422,
    #                         detail=f"=== Неверный токен: {upd_bot_model.token_tg= }, Ошибка: {bot_info} ===")
# ================================================
    # if not bot_info:
    #     raise HTTPException(status_code=422,
    #                         detail=f"=== Неверная Установка : {upd_bot_model.active.value= },
#                         Ошибка: {bot_info=} ===")

# ================================================
# def get_bot_by_port(bot: dict = Body(),
# def get_bot_by_port(bot: SBotGetByPort = Depends(checker),
# def get_bot_by_port(bot: SBotGetByPort = Depends(),
# ================================================
# def checker(data: str = Form(...)):
#     try:
#         return SBotGetByPort.model_validate_json(data)
#     except ValidationError as e:
#         raise HTTPException(
#             detail=jsonable_encoder(e.errors()),
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         )
# ================================================
# router = APIRouter(prefix="", tags=["Bots"])
# router = APIRouter(prefix="")
# ================================================
# ---------------------------------------------
    # stmt_upd = (update(BotsOrm)
    #             .where(BotsOrm.web_server_port == data.get("web_server_port"))
    #             .values(description="7777 descr----", state=data.get('state').name))
    #
    # bot_model = db_session.execute(stmt_upd)
    # print("===1======", bot_model)
    #
    # if bot_model is None:
    #     raise HTTPException(status_code=404, detail="Бот не найден")
    #
    # db_session.commit()
    # bot = SBot.model_validate(bot_model)
    # print("===2======", bot)
    # return bot


# ---------------------------------------------
#     data = bot.model_dump()
#     # stmt = select(BotsOrm).where(BotsOrm.web_server_port == data['web_server_port'])
#
#     stmt_upd = (update(BotsOrm)
#                 .where(BotsOrm.web_server_port == data.get("web_server_port"))
#                 .values(description="7777 descr----", state=data.get('state').name))
#
#     bot_model = db_session.execute(stmt_upd)
#     print("===1======", bot_model)
#
#     if bot_model is None:
#         raise HTTPException(status_code=404, detail="Бот не найден")
#
#     db_session.commit()
#     bot = SBot.model_validate(bot_model)
# ---------------------------------------------
    # stmt = select(BotsOrm).where(BotsOrm.web_server_port == data['web_server_port'])
    # result = db_session.execute(stmt)
    # bot_model = result.scalar()
    # print("===1======", bot_model)
    #
    # if bot_model is None:
    #     raise HTTPException(status_code=404, detail="Бот не найден")
# ---------------------------------------------
    # db_session.commit()  # сохраняем изменения
    # db_session.refresh(bot)
    # return bot
    # db_session.execute(stmt_upd)
    # upd_bot_model.state = data.get('state').name  # второй способ обновле
    # stmt_upd = (update(BotsOrm)
    #         .where(BotsOrm.web_server_port == data.get("web_server_port"))
    #         .values(description="66 description----", state=data.get('state').name))
# ---------------------------------------------

# ==========================================
# ==========================================
    # print("===1_1==DATA==get(web_server_port)+++++===", data.get("web_server_port"))
    # # upd_bot_model = db_session.query(BotsOrm).filter(BotsOrm.web_server_port == 15007)
    # result = db_session.query(BotsOrm).filter(BotsOrm.web_server_port == data.get("web_server_port"))
    # upd_bot_model = result.scalars().all()
    # print("===1=BOT MODEL+++++=====", upd_bot_model)
    # if upd_bot_model is None:
    #     raise HTTPException(status_code=404, detail="Бот не найден")

    # # ========================
    # # ======= RAB_1=================
    #     stmt = (update(BotsOrm)
    #             .where(BotsOrm.web_server_port.__eq__(data.get("web_server_port")))
    #             .values(description="66 description----", token_tg="66-qqqqqqqqqqqqq", state=data.get('state').value))
    #     print("===2=BOT stmt+++++=====", stmt)
    #     upd_bot_model = db_session.execute(stmt)
    #     db_session.commit()
    #     print("===3=BOT upd_bot_model+++++=====", upd_bot_model)
    # ==========END RAB_1==============
    # # ========================

    # stmt = select(BotsOrm).where(BotsOrm.web_server_port.__eq__(data.get("web_server_port")))
    # stmt = select(BotsOrm).where(BotsOrm.web_server_port.__eq__(15007))
# ==========================================
    # for bot_model in result:
    #     print("======1555===== bot_model== ", bot_model)

    # print("===1_5======", db_session.scalar(stmt).web_server_port)

    # for b in db_session.scalars(stmt):
    #     print("=======bbbbbbbbbb====== ", b)
    #
    # upd_bot_model = db_session.execute(stmt)
    # print("===4=BOT upd_bot_model+++++=====", upd_bot_model)

    # statement = select(BotsOrm).filter_by(web_server_port=15006)
    # upd_bot_model = db_session.execute(statement).scalars().all()
    # print("===5=BOT upd_bot_model+++++=====", upd_bot_model)
    #     print("===0===db_sess====", db_session.info)
    #     print("===1=BOT MODEL+++++=====", upd_bot_model)
    #     for row in upd_bot_model:
    #         print("======ROW===", row)
    # # ========================

    # upd_bot_model = db_session.get(BotsOrm)
    # upd_bot_model = db_session.get(BotsOrm)
    # upd_bot_model = db_session.execute(upd_bot_model).first()
    # print("===2=BOT MODEL+++++=====", upd_bot_model)

    # db_session.query(BotsOrm).update({"state": "Not_Active"})

    # db_session.flush()
    # print("===3=BOT MODEL+++++=====", upd_bot_model)
    # db_session.commit()

# ==========================================
    # prefix="/bots",
# ===============================================
# # def edit_bot(data=Body(), db: Session = Depends(get_db)):
# @router.put("/api/bots")
# def edit_bot(bot: SBotUpdate = Depends(), db_session: Session = Depends(get_db)) -> SBot:
#     data = bot.model_dump(exclude_unset=True)
#     print("===== DATA=====", data)
#     new_bot_model = BotsOrm(**data)
#     print("===== new_bot_model=====", new_bot_model)
#     db_session._update_impl(new_bot_model)
# ===============================================
# @app.get("/api/bots/{id}")
# def get_bot(idpk, db_session: Session = Depends(get_db)) -> SBot:
#     bot_model = db_session.query(BotsOrm).filter(BotsOrm.id == idpk).first()
#     # if bot_model is None:
#     #     raise HTTPException(status_code=404, detail="Бот не найден")
#     try:
#         bot = SBot.model_validate(bot_model)
#     except ValidationError as exc:
#         print("===VALOD EERRR=== ", repr(exc.errors()[0]['type']))
#         raise HTTPException(status_code=404, detail="Бот не найден")
#     return bot
# ===================================
#     try:
#         db_session.flush()
#         db_session.commit()
#         new_bot = SBot.model_validate(new_bot_model)
#         return new_bot
#     except exc.IntegrityError as e:
#         print(f"\n==== Бот c таким xxxxx уже есть ======\n {e.args}\n\n")
#         db_session.rollback()
#         raise HTTPException(status_code=422, detail=f"Не верные данные: {e.args}")

# ===================================
# # def insert_bot(data=Body(), db_session: Session = Depends(get_db)) -> BotSchAdd:
# @app.post("/api/bots")
# def insert_bot(data=Body(), db_session: Session = Depends(get_db)) -> BotsOrm:
#     print("====data==:", data)
#     bot = BotsOrm(web_server_host=data.get("web_server_host"),
#                   web_server_port=data.get("web_server_port"),
#                   description=data.get('description'),
#                   state=data.get('state'),
#                   token_tg=data.get('token_tg'),
#                   base_webhook_url=data.get('base_webhook_url'))
#     db_session.add(bot)
#     db_session.commit()
#     db_session.refresh(bot)
#     return bot
# ==========================================

    # if bot is None:
    #     return JSONResponse(status_code=404, content={"message": "Бот не найден"})
    #     return JSONResponse(status_code=404, content={"message": "Бот не найден"})
# return JSONResponse(status_code=404, content={"message": "Пользователь не найден"})
    # если пользователь найден, отправляем его
# ==========================================
# @app.get("/")
# def main():
#     return FileResponse("public/index.html")
# ==========================================
# @app.post("/api/bots")
# def insert_bot(data=Body(), db_session: Session = Depends(get_db)) -> BotSchAdd:
#     print("====data==:", data)
#     bot = BotsOrm(web_server_host=data.get("web_server_host"),
#                   web_server_port=data.get("web_server_port"),
#                   description=data.get('description'),
#                   state=data.get('state'),
#                   token_tg=data.get('token_tg'),
#                   base_webhook_url=data.get('base_webhook_url'))
#     db_session.add(bot)
#     db_session.commit()
#     db_session.refresh(bot)
#     return bot
# ==========================================
# @app.get("/api/bots/{id}")
# def get_bot(idpk, db_session: Session = Depends(get_db)) -> JSONResponse | Type[BotsOrm]:
#     # получаем пользователя по id
#     bot = db_session.query(BotsOrm).filter(BotsOrm.id == idpk).first()
#     # если не найден, отправляем статусный код и сообщение об ошибке
#     if bot is None:
#         return JSONResponse(status_code=404, content={"message": "Бот не найден"})
#         # return JSONResponse(status_code=404, content={"message": "Бот не найден"})
#     # если пользователь найден, отправляем его
#     return bot
# ==========================================
# @app.post("/api/bots", response_model=BotSchAdd) или:
# def insert_bot(data=Body(), db_session: Session = Depends(get_db)) -> BotSchAdd:
# ==========================================
# js_req = [
#     {'web_server_host': '127.0.0.1',
#      'web_server_port': 15007,
#      'description': 'fff description',
#      'state': 'Active',
#      'token_tg': '677777:token_tg',
#      'base_webhook_url': 'https://178.1.1.1:8443/bot/'
#      },
# ]
#
# js_req1 =\
#     {"web_server_host": "127.0.0.1",
#      "web_server_port": 15007,
#      "description": "fff description",
#      "state": "Active",
#      "token_tg": "677777:token_tg",
#      "base_webhook_url": "https://178.1.1.1:8443/bot/"
#      }
# ==========================================
# Then you can run it with Uvicorn:
# uvicorn main:app --host 0.0.0.0 --port 12000 --reload

# uvicorn db.main:app --reload
# uvicorn db.main:app --port 12000 --reload
# uvicorn main_fastapi:app --host 0.0.0.0 --port 80
#

# And then, you can open your browser at http://127.0.0.1:8000/docs
