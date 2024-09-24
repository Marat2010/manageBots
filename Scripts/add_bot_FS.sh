#!/bin/bash

# Подготовка шаблона для бота
# Запуск в шелле: ./Scripts/add_bot_FS.sh "Yes" "/bot/"
# Запуск сервиса, службы (SYSTEMD) для бота ==="
# Первый параметр $1 - (Yes, No) добавить или удалить, $2 - WEBHOOK_PATH (в примере "/bot/"),
# $3 - token_tg, токен ТГ (в примере 66151xxxxx:AAHbuZTxxxxxxxxxxxxxxxxJqGJnJQ)
# $4 - web_server_host, $5 - web_server_port

#=======================================================
if [ "$USER" != "root" ]; then
    echo "Для выполнения скрипта нужны права sudo, права суперпользователя"
fi

#=======================================================
if [ -z "$PROJECT_NAME" ]; then
  printf "Нет переменной окружения 'PROJECT_NAME', необходимо перезайти в терминале!\n"
  exit 1
fi

#=======================================================
#cd "/home/marat/PycharmProjects/manageBots/" || { exit 1; }
#----- Менять на вверх когда запуск у себя --------
cd "$HOME/$PROJECT_NAME" || { exit 1; }

port=$5
printf "=== Установлен: WEB_SERVER_PORT=%s\n" "$port"
token=$3
printf "=== Установлен: TOKEN_TG=%s\n" "$token"

#=======================================================
if [ "$1" == "Yes" ]; then
  mkdir "./our_Bots/bot_$port" || { echo " !!! Такой бот существует !!!"; exit 1;}

  cp ./our_Bots/bot_example/main_example.py ./our_Bots/bot_"$port"/main.py
  cp ./our_Bots/bot_example/config_bots_example.py ./our_Bots/bot_"$port"/config_bots.py
  sed -i "s/SetPort/$port/" our_Bots/bot_"$port"/config_bots.py

  #=======================================================
  printf "\n === Формирования файла окружения для бота ===\n"
  echo "# =================== DB ============================
  DATABASE_URL_SQLITE='./DB/mb.sqlite3'

  #============ TELEGRAM (WEB SERVER local) ===========
  WEB_SERVER_PORT=$port  # Для каждого бота, должен быть уникален, начиная с 9001 ..
  WEB_SERVER_HOST=$4
  TOKEN_TG=$token

  # ========== TELEGRAM settings for bots ============
  SELF_SSL=True  # Для случаев, когда нет нормального сертификата на домен или IP.

  # == Для автоматического определения IP адреса закомментируйте эту строку!!! ==
  # PUBLIC_IP='178.1.1.1'  # Внешний IP адрес или имя домена (для IP должен быть SSL)

  # == BASE_WEBHOOK_URL формируется из PUBLIC_IP, поэтому можно убрать
  # BASE_WEBHOOK_URL = 'https://178.111.111.111:8443'

  WEBHOOK_PATH_BASE='$2'  # Часть полного пути вебхук урла /bot/6615142110:AAHbuZ...
  WEBHOOK_SECRET='change_secret_2024'  # Разрешены только символы A-Z, a-z, 0-9, _и -.
  " > ./our_Bots/bot_"$port"/.env_bot

  #=======================================================
  echo
  echo "=== Каталог бота: $PWD/our_Bots/bot_$port ==="
  ls -al "$PWD/our_Bots/bot_$port"

  #=======================================================
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

  echo "=== Запуск бота (bot_$port) как службу"
  sudo systemctl daemon-reload
  sudo systemctl enable bot_"$port".service
  sudo systemctl start bot_"$port".service

elif [ "$1" == "No" ]; then
  printf "\n=== Удаляем бота из конфигурации Nginx ===\n"
  rm -v /etc/nginx/conf.d/bots/bot_"$3".conf  # bot_"$5".conf - Можно указать port, а не токен

  printf "\n=== Делаем архив и Удаляем бота из файловой системы ===\n"
  date_arh="$(date +%d-%m-%Y_%T)"
  tar -zcvf our_Bots/Archive/bot_"$port"_"$date_arh".tar.gz -X ./our_Bots/Archive/Script/exclude_archive.txt ./our_Bots/bot_"$port"
  echo
  echo "=== Архив здесь: '$HOME/$PROJECT_NAME/our_Bots/Archive/bot_${port}_${date_arh}.tar.gz'"
  sudo rm -rfv ./our_Bots/bot_"$port"

  printf "\n=== Остановка сервиса (службы) бота ===\n"
  sudo systemctl stop bot_"$5"
  sudo systemctl disable bot_"$5"
  sudo rm -v "/lib/systemd/system/bot_$port.service"
  sudo systemctl daemon-reload
else
  printf "\n=== Неверное состояние бота (должно быть Yes или No) ===\n"
fi


#======================================================
#======================================================
#======================================================
#  tar -zcvf .My_Archive/"$proj"_"$date_arh".tar.gz -X ./.My_Archive/Script/exclude_archive.txt "$proj"
#======================================================
#lsof -i|grep 9001
#ss -nultp |grep 9001
#======================================================

