#!/bin/bash

printf "\n\n===================================\n"
printf "\n=== Подготовка шаблона для бота ===\n"
printf "\n===================================\n\n"
#echo "=== Запуск сервиса, службы (SYSTEMD) для бота ==="

#=======================================================
if [ -z "$PROJECT_NAME" ]; then
  printf "Нет переменной окружения 'PROJECT_NAME', необходимо перезайти в терминале!\n"
  exit 1
fi

#=======================================================
read -rp "=== Укажите на каком порту будет работать бот (WEB_SERVER_PORT) [9001]: " port
if [ -z "$port" ]; then port=9001; fi
printf "    Установим: WEB_SERVER_PORT=%s\n\n" "$port "

read -rp "=== Укажите токен бота (TOKEN_TG) [66xx:AA......JQ]: " token
if [ -z "$token" ]; then token=66xx:AA......JQ; fi
printf "    Установим: TOKEN_TG=%s\n" "$token"

#=======================================================
#cd "/home/marat/PycharmProjects/manageBots/" || { exit 1; }
#mkdir "./our_Bots/bot_$port" || { echo " !!! Такой бот существует !!!!!"; exit 1;}
#----- Менять на вверх когда запуск у себя --------
cd "$HOME/$PROJECT_NAME" || { exit 1; }
mkdir "./our_Bots/bot_$port" || { echo " !!! Такой бот существует !!!"; exit 1;}

cp ./our_Bots/bot_example/main_example.py ./our_Bots/bot_$port/main.py
cp ./our_Bots/bot_example/config_bots_example.py ./our_Bots/bot_$port/config_bots.py
sed -i "s/SetPort/$port/" our_Bots/bot_$port/config_bots.py

#=======================================================
printf "\n === Формирования файла окружения для бота ===\n"
echo "# =================== DB ============================
DATABASE_URL_SQLITE='./DB/mb.sqlite3'

#============ TELEGRAM (WEB SERVER local) ===========
WEB_SERVER_PORT=$port  # Для каждого бота, должен быть уникален, начиная с 9001 ..
WEB_SERVER_HOST=127.0.0.1
TOKEN_TG=$token

# ========== TELEGRAM settings for bots ============
SELF_SSL=True  # Для случаев, когда нет нормального сертификата на домен или IP.

# == Для автоматического определения IP адреса закомментируйте эту строку!!! ==
# PUBLIC_IP='178.1.1.1'  # Внешний IP адрес или имя домена (для IP должен быть SSL)

# == BASE_WEBHOOK_URL формируется из PUBLIC_IP, поэтому можно убрать
# BASE_WEBHOOK_URL = 'https://178.111.111.111:8443'

WEBHOOK_PATH_BASE='/bot/'  # Часть полного пути вебхук урла /bot/6615142110:AAHbuZ...
WEBHOOK_SECRET='change_secret_2024'  # Разрешены только символы A-Z, a-z, 0-9, _и -.
" > ./our_Bots/bot_$port/.env_bot

#=======================================================
echo
echo "=== Каталог бота: $PWD/our_Bots/bot_$port ==="
ls -al "$PWD/our_Bots/bot_$port"

#=======================================================
echo
read -rp "=== Запустить бота (bot_$port ) как службу? [y/N]: " run_service

if [ "$run_service" == "y" ]; then
    echo "
    [Unit]
    Description=Aiogram3 bot_$port service
    After=multi-user.target
     
    [Service]
    User=root
    Group=root
    Type=idle
    Restart=on-failure

    EnvironmentFile=/etc/environment

    ExecStart=/usr/bin/bash -c 'cd $HOME/$PROJECT_NAME && source .venv/bin/activate && python ./our_Bots/bot_$port/main.py'

    [Install]
    WantedBy=multi-user.target
    " > "$HOME/$PROJECT_NAME/our_Bots/bot_$port/bot_$port.service"

    sudo cp "$HOME/$PROJECT_NAME/our_Bots/bot_$port/bot_$port.service" "/lib/systemd/system/bot_$port.service"

    sudo systemctl daemon-reload
    sudo systemctl enable bot_"$port".service
    sudo systemctl start bot_"$port".service
fi


#======================================================
#======================================================
#======================================================
#lsof -i|grep 9001
#ss -nultp |grep 9001
#======================================================
##=============== Logs ================================
#LOG_Bot_File='./our_Bots/bot_$port/bot_$port.log'
##=====================================================
#======================================================
#    Environment='PROJECT_NAME=manageBots'
#    ExecStart=/bin/bash -c 'cd $HOME/$PROJECT_NAME && source .venv/bin/activate && ./our_Bots/bot_$port/Run_bot.sh'
#cp "./our_Bots/bot_example/.env_example_bot" "./our_Bots/bot_$port/.env_bot"
#======================================================
