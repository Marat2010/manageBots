# import logging
from appMB.config_m import logging
from typing import List, Type
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import exc

from appMB.config_m import BASE_WEBHOOK_URL, config_M
from appMB.database import get_db
from appMB.models import BotsOrm, ActiveBot, BaseWebhookUrlOrm
from appMB.schemas import (SBot, SBotGetByPort, SBotUpdateByPort,
                           SBotGetByToken, SBotUpdateByToken, SBotDel, SBotUpd, SUrlAdd, SUrl, SBotAddOwner,
                           )
from appMB.utils import change_state_bot, ServerPort

router = APIRouter(prefix="/api/bots")


def add_first_urls():
    generator = get_db()
    db_session = next(generator)

    url_model = db_session.query(BaseWebhookUrlOrm).filter(BaseWebhookUrlOrm.url == BASE_WEBHOOK_URL).first()

    if url_model is None:
        new_url_model = BaseWebhookUrlOrm(**{"url": BASE_WEBHOOK_URL})
        db_session.add(new_url_model)

        db_session.flush()
        db_session.commit()


@router.get("", summary="Получить всех ботов", tags=["Standard"])
def get_bots(db_session: Session = Depends(get_db)) -> List[SBot]:
    bots_models = db_session.query(BotsOrm).all()
    bots = [SBot.model_validate(bot_model) for bot_model in bots_models]
    return bots


@router.get("/urls", summary="Получить все базовые части вебхук url-ов ", tags=["Standard"])
def get_urls(db_session: Session = Depends(get_db)) -> List[SUrl]:
    url_models = db_session.query(BaseWebhookUrlOrm).all()
    urls = [SUrl.model_validate(url_model) for url_model in url_models]
    return urls


@router.get("/{idpk}", summary="Получить бота по 'id'", tags=["Standard"])
def get_by_id(idpk, db_session: Session = Depends(get_db)) -> SBot:
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.id == idpk).first()
    if bot_model is None:
        logging.warning(f"\n\n  === Бот не найден {idpk= } ===\n")
        raise HTTPException(status_code=404, detail="Бот не найден")
    bot = SBot.model_validate(bot_model)
    return bot


# def update_by_id(idpk, bot: SBotUpd,
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
    return upd_bot(bot_model, data, db_session)


@router.delete("/del/{idpk}", summary="Удалить бота по 'id'", tags=["Standard"])
def delete_by_id(idpk, db_session: Session = Depends(get_db)) -> SBotDel:
    bot_model = db_session.query(BotsOrm).filter(BotsOrm.id == idpk).first()
    return del_bot(bot_model, db_session)


# =======================================================
# ============== For Manage bots ========================
# =======================================================
@router.post("/add_base_url", summary="Добавить базовый вебхук урл", tags=["Manage Bots"])
def add_url_bwh(url: SUrlAdd = Depends(), db_session: Session = Depends(get_db)) -> SUrl:
    data = url.model_dump()
    new_url_model = BaseWebhookUrlOrm(**data)
    db_session.add(new_url_model)

    logging.info(f"\n\n  === Добавление базового вебхук урла: ===\n{new_url_model=} \n")

    try:
        db_session.flush()
        db_session.commit()
    except exc.IntegrityError as e:
        logging.error(f"\n\n  === Не верные данные: ===\n{e.args=:}\n")
        db_session.rollback()
        raise HTTPException(status_code=422, detail=f"Не верные данные: {e.args}")

    new_url = SUrl.model_validate(new_url_model)
    return new_url


# def add_bot(bot: SBotAdd = Depends(), db_session: Session = Depends(get_db)) -> SBot:
@router.post("/add_bot", summary="Добавить Нового бота для 'OWNER'", tags=["Manage Bots"])
def add_bot_owner(bot: SBotAddOwner, db_session: Session = Depends(get_db)) -> SBot:
    data = bot.model_dump()
    data.update({"web_server_host": config_M.WEB_SERVER_HOST})
    data.update({"web_server_port": ServerPort.get_web_server_port()})
    data.update({"url_bwh_id": 1})
    data.update({"active": ActiveBot.Yes})  # Необходимо установить для добавления вебхуку и бота
    # data.update({"active": ActiveBot.No})
    logging.info(f"\n\n  ===== {data=} =====\n")
    new_bot_model = BotsOrm(**data)
    db_session.add(new_bot_model)

    try:
        db_session.flush()
        db_session.commit()
    except exc.IntegrityError as e:
        logging.error(f"\n\n  === Не верные данные: ===\n{e.args=:}\n")
        # new_bot_model.active = ActiveBot.No  # Необходимо, чтобы отключить вебхук и удалить бота
        # change_state_bot(new_bot_model, "Del")  # Отключение бота от вебхука
        db_session.rollback()
        ServerPort.set_web_server_port(new_bot_model.web_server_port-1)
        raise HTTPException(status_code=422, detail=f"Не верные данные: {e.args}")

    # ======================================================================
    logging.info(f"\n\n  === Добавление бота: ===\n{new_bot_model=} \n")
    bot_info = change_state_bot(new_bot_model, "Add")  # Отключение или включение бота
    new_bot_model.bot_username = bot_info.username
    # ======================================================================
    if new_bot_model.bot_username is None:
        new_bot_model.bot_username = "Бот еще не запускался"

    new_bot = SBot.model_validate(new_bot_model)
    ServerPort.set_web_server_port(new_bot_model.web_server_port)  # Запомнить последний использованный порт

    return new_bot


# =======================================================
# ============== For Manage bots ========================
# ============ by web_server_port =======================

# @router.post("/get_by_port", tags=["Manage Bots by web_server_port"],
@router.get("/get_by_port", tags=["Manage Bots by web_server_port"],
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

# @router.post("/get_by_token", tags=["Manage Bots by token_tg"],
@router.get("/get_by_token", tags=["Manage Bots by token_tg"],
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
# def upd_bot(bot_model: Type[BotsOrm], data: dict, db_session: Session = Depends(get_db)) -> SBot | dict:
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


# def del_bot(bot_model: Type[BotsOrm], db_session: Session = Depends(get_db)) -> SBotDel:
def del_bot(bot_model: BotsOrm, db_session: Session = Depends(get_db)) -> SBotDel:
    if bot_model is None:
        logging.warning(f"\n\n  === Бот не найден ===\n")
        raise HTTPException(status_code=404, detail="Бот не найден")

    bot_model.active = ActiveBot.No  # Необходимо, чтобы отключить вебхук и удалить бота
    bot_info = change_state_bot(bot_model, "Del")  # Отключение бота от вебхука
    bot_model.bot_username = bot_info.username  # МОЖНО УБРАТЬ

    db_session.delete(bot_model)
    db_session.commit()
    bot_model.deleted = True  # Выставляем, чтобы в ответе было видно, что удален.
    bot = SBotDel.model_validate(bot_model)
    ServerPort.set_web_server_port(bot_model.web_server_port)  # Запомнить последний использованный порт
    return bot  # Можно сразу 'SBot.model_validate(bot_model)'


# ==================================================================
# ==================================================================
# Добавление бота с учетом указания всех данных (порт, описание, ...)
# # def add_bot(bot: SBotAdd, db_session: Session = Depends(get_db)) -> SBot:
# @router.post("/add", summary="Добавить нового бота", tags=["Manage Bots"])
# def add_bot(bot: SBotAdd = Depends(), db_session: Session = Depends(get_db)) -> SBot:
#     data = bot.model_dump()
#
#     new_bot_model = BotsOrm(**data)
#
#     # raise HTTPException(status_code=422,
#     #                     detail=f"----=== Проверка ДАННЫХ !!!=======-----\n"
#     #                            f" Ошибки: '{data=}'\n {new_bot_model=} ===")
#
#
#     # url = (db_session.query(BaseWebhookUrlOrm).
#     #        filter(BaseWebhookUrlOrm.id == data.get("url_bwh")).first())
#
#     # new_bot_model.url_bwh_id = url.id
#     # new_bot_model.url_bwh = url
#     # if new_bot_model.url_bwh_id is None:
#     #     logging.info(f"\n\n  ---qqqq--------===== {new_bot_model=} =====--------------\n")
#     db_session.add(new_bot_model)
#
#     # ======================================================================
#     # logging.info(f"\n\n  === Добавление бота: ===\n{new_bot_model=} \n")
#     # bot_info = change_state_bot(new_bot_model)  # Отключение или включение вебхука для бота
#     # new_bot_model.bot_username = bot_info.username
#     # ======================================================================
#     new_bot_model.bot_username = "Test USER TG"
#
#     try:
#         db_session.flush()
#         db_session.commit()
#     except exc.IntegrityError as e:
#         logging.error(f"\n\n  === Не верные данные: ===\n{e.args=:}\n")
#         db_session.rollback()
#         raise HTTPException(status_code=422, detail=f"Не верные данные: {e.args}")
#
#     # new_bot_model.url_bwh = data.get("url_bwh_id")
#     logging.info(f"\n\n  ---5--------===== {new_bot_model=} =====--------------\n")
#
#     new_bot = SBot.model_validate(new_bot_model)
#     return new_bot
# ================================================
