# === В РАЗРАБОТКЕ !!! ===
### === Необходимо проверить на VPS!!! ===

---

## Система управления ботами - СУБота&#169; 😊
### API - Менеджер ботов СУБота©️  (manageBots)
### (FastAPI+Aiogram3+Webhook+SSL на VPS/VDS): 

<u>***!!! Осторожно, скрипты могут затереть ваши файлы!!!***</u>  
<u>***Предполагается установка на вновь созданный сервер!***</u>  

---
### Описание
Полный цикл работ по размещению СУБотами на Aiogram3 c webhook, SSL на VPS/VDS.  
Система управления реализовано на API FastAPI, БД SQLite (возможно использовать любую СУБД - использована библиотека SQLAlchemy)  
Пока НЕ Проверено на ОС серверов .... Timeweb, Рег.ру:  Ubuntu 20.04, Ubuntu 22.04.

1. Подключаемся к серверу `ssh root@xxx.xxx.xxx.xxx` и выполняем последовательно все команды.    

2. Скачиваем и запускаем первый скрипт, выполним команду:  
    ```
    wget -O ./0_prepare.sh https://raw.githubusercontent.com/Marat2010/manageBots/master/Scripts/0_prepare.sh && chmod +x 0_prepare.sh && ./0_prepare.sh
    ```
   Скрипт подготовить все, для запуска менеджера: 
   - скачает репозиторий
   - установку и настройку nginx
   - установку вирт.окружения, пакетов apt, пакетов из requerements.txt
   - необходимые скрипты.
   - ...

3. Для подготовки ботов необходимо запускать скрипт:
   ```
   ./manageBots/Scripts/1_prepare_bots.sh
   ```
   Для запуска, необходимо перезайти, выйти и снова подключиться. При каждом запуске формируется каталог 'bot_Номер порта'.
   В котором необходимо разместить своего бота.   
Каталог представляем собой шаблон, в котором настроены переменные окружения
   
   
Далее начинается основная работа с ботами.  
После запуска первого скрипта (0_prepare.sh), на экран выйдут ссылки для управления.
Необходимо перейти по ссылки в API, где происходит управление ботами.




---
 
### Продолжение следует ....
\
\
\
\
<br>
&nbsp;&nbsp;&nbsp;&nbsp;©Marat2010



