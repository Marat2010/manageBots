""" Примеры запросов к API """

import requests


# ========= Получение всех ботов =========================
def get_all_bots():
    import requests
    headers = {
        'accept': 'application/json',
    }
    response = requests.get('http://127.0.0.1:8900/api/bots', headers=headers)
    return response


# ========= Общее Обновление =========================
def update_bot_by_id(data):
    headers = {
        'accept': 'application/json',
    }
    params = data
    # params = {
    #     'idpk': bot_id,
    #     'web_server_host': '127.0.0.1',
    #     'web_server_port': '9001',
    #     'description': 'Бот делает ...',
    #     'active': 'Нет',
    #     'token_tg': '32ewew:323',
    #     'url_bwh_id': '1',
    # }
    response = requests.put('http://127.0.0.1:8900/api/bots/update', params=params, headers=headers)
    return response


# ============ Добавление бота в систему ======================
def add_bot_by_token(token):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    json_data = {
        'token_tg': token,
    }
    response = requests.post('http://127.0.0.1:8900/api/bots/add_bot', headers=headers, json=json_data)
    return response


# ============ Включение, выключение бота по порту======================
def activate_bot_by_port(web_server_port, active):
    headers = {
        'accept': 'application/json',
    }
    params = {
        'web_server_port': web_server_port,
        'active': active,   # 'active': 'Нет' или 'Да'
    }
    response = requests.patch('http://127.0.0.1:8900/api/bots/update_active_by_port', params=params, headers=headers)
    return response


# ============ Включение, выключение бота по токену======================
def activate_bot_by_token(token, active):
    headers = {
        'accept': 'application/json',
    }
    params = {
        'token_tg': token,
        'active': active,   # 'active': 'Нет' или 'Да'
    }
    response = requests.patch('http://127.0.0.1:8900/api/bots/update_active_by_token', params=params, headers=headers)
    return response


# ============ Удаление бота из системы ======================
def del_bot_by_port(web_server_port):
    headers = {
        'accept': 'application/json',
    }
    params = {
        'web_server_port': web_server_port,
    }
    response = requests.delete('http://127.0.0.1:8900/api/bots/del_by_port', params=params, headers=headers)
    return response


# =======================================================
# =======================================================
# ========= Получение всех ботов (пример) ================
print("==== Получение всех ботов (пример)========")

resp = get_all_bots()
print(f"== {resp.json()=} ==")


# ========= Общее Обновление (пример) =========================
print("==== Общее Обновление (пример) ========")

# data_bot = {
#     'idpk': 1,
#     'web_server_host': '127.0.0.1',
#     'web_server_port': '9001',
#     'description': '1 Бот делает ...',
#     'active': 'Нет',
#     'token_tg': '32ewew:323',
#     'url_bwh_id': '1',
# }
#
# resp = update_bot_by_id(data_bot)
#
# data_json = resp.json()
# print(f"== {data_json=} ==")

# ========= Добавление бота в систему (пример) ===============
print("==== Добавление бота в систему (пример) ========")

# resp = add_bot_by_token("6189xxxx:AAEdN................FB-MtAQ")
# # resp = add_bot_by_token("6267xxxxx:AAHuG.................YnpKUT4")
# # resp = add_bot_by_token("6479xxxxx:AAFAi3.................CWtCVzi0")
# # resp = add_bot_by_token("6615xxxxx:AAHbuZ.................JqGJnJQ")
#
# data_json = resp.json()
# print(f"== {data_json=} ==")

# ========= Включение, выключение бота по порту (пример) =================
print("==== Включение, выключение бота по порту (пример) ========")

# resp = activate_bot_by_port(9001, "Да")
# # resp = activate_bot_by_port(9001, "Нет")
#
# data_json = resp.json()
# print(f"== {data_json=} ==")

# ========= Включение, выключение бота по токену (пример) =================
print("==== Включение, выключение бота по токену (пример) ========")

resp = activate_bot_by_token("6189xxxxx:AAEdN3................B-MtAQ", "Да")
# resp = activate_bot_by_token("6189xxxx:AAEdN..................B-MtAQ", "Нет")

data_json = resp.json()
print(f"== {data_json=} ==")

# ========= Удаление бота из системы (пример) ===============
print("==== Удаление бота из системы (пример) ========")

# resp = del_bot_by_port(9003)
# data_json = resp.json()
# print(f"== {data_json=} ==")


# ==================================================
# ==================================================
# ==================================================
