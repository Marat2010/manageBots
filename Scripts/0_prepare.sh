#!/bin/bash

# ===== Скрипт для предварительной подготовки сервера VPS =====

echo "=== !!! Выполнять под пользователем root !!! ==="

if [ "$USER" != 'root' ]; then
    echo "=== Вы пользователь '$USER', необходимо запустить под пользователем: 'root'!"
    exit 1
fi

# ===== Смена пароля root-а =====
echo
read -rp "=== Сменить у пользователя 'root' пароль? [y/N] - по умолчанию нет(Enter): " change_passwd_root

if [ "$change_passwd_root" == "y" ]
then
    passwd root
fi

echo "===== Установка пакетов ====="

apt update

echo
read -rp "=== Установить FTP сервер? [y/N] - по умолчанию нет(Enter): " confirm
if [ "$confirm" == "y" ]; then
    echo "=== Установка FTP сервера ==="
    echo "=== Инструкция: https://help.reg.ru/support/servery-vps/oblachnyye-servery/ustanovka-programmnogo-obespecheniya/kak-ustanovit-ftp-server-na-ubuntu ==="
    apt -y install vsftpd
    systemctl enable vsftpd.service
fi

echo
read -rp "=== Установить Midnight Commander? [y/N] - по умолчанию нет(Enter) " confirm
if [ "$confirm" == "y" ]; then
    echo "=== Установка Midnight Commander ==="
    apt -y install mc
fi

echo
read -rp "=== Установить Lynx? [y/N] - по умолчанию нет(Enter) " confirm
if [ "$confirm" == "y" ]; then
    echo "=== Установка Lynx ==="
    apt -y install lynx
fi

echo
read -rp "=== Установить sqlite3 для терминала? [y/N] - по умолчанию нет(Enter) " confirm
if [ "$confirm" == "y" ]; then
    apt install sqlite3
    echo
    echo "============================================================="
    echo "=====      Установлен sqlite3 для терминала              ====="
    echo "=== # sqlite3 DB/mb.sqlite3 - подключение к БД            ==="
    echo "=== sqlite> select * from bots; - просмотр таблицы 'bots' ==="
    echo "============================================================="
    read -rp "=====  Если прочитали, нажмите enter для продолжения ===== "
fi

echo
read -rp "=== Установить прокси веб-сервер Nginx? [y/N] - по умолчанию нет(Enter) " confirm
if [ "$confirm" == "y" ]; then
    echo "=== Установка пакета Nginx ==="
    sudo apt -y install nginx
    sudo systemctl enable nginx
fi

echo
read -rp "=== Установить модуль VENV (python3-venv)? [y/N] - по умолчанию нет(Enter) " confirm
if [ "$confirm" == "y" ]; then
  echo "=== Установка модуля VENV (python3-venv) ==="
  apt -y install python3-venv
fi

echo
echo "=== FTP: Настройка сервера ==="
cp /etc/vsftpd.conf /etc/vsftpd.conf.original

echo "
listen=YES
listen_ipv6=NO
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
use_localtime=YES
xferlog_enable=YES
connect_from_port_20=YES
xferlog_file=/var/log/vsftpd.log
xferlog_std_format=YES
chroot_local_user=YES
allow_writeable_chroot=YES
local_root=/
pam_service_name=vsftpd
#userlist_enable=YES
userlist_file=/etc/vsftpd.userlist
#userlist_deny=NO
userlist_deny=YES

rsa_cert_file=/etc/ssl/private/vsftpd.pem
rsa_private_key_file=/etc/ssl/private/vsftpd.pem
ssl_enable=YES
" > /etc/vsftpd.conf

printf "\n\n=== FTP: Формирование SSL-сертификата  ===\n"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/vsftpd.pem -out /etc/ssl/private/vsftpd.pem -subj "/C=RU/ST=RT/L=KAZAN/O=Home/CN=1/emailAddress=em"

#======================================================

echo
read -rp "=== Разрешить доступ root-у по ftp? [y/N] - по умолчанию нет(Enter) " confirm
if [ "$confirm" == "y" ]; then
  cp /etc/ftpusers /etc/ftpusers_"$(date +%d-%m-%Y_%T)"
  sed -i 's/root/# root/' /etc/ftpusers
  cat /etc/ftpusers
  echo
  echo "========================================================================================="
  echo "==== Для отмены доступа root-a по ftp раскомментируйте '# root' в файле /etc/ftpusers ==="
  echo "====        И перезапустите: systemctl restart vsftpd.service                                 ==="
  echo "========================================================================================="
  read  -rp "=====    Если прочитали, для продолжения нажмите enter               ===== "
fi

#======================================================

echo
read -rp "=== Отключить dhclient6? [y/N] - по умолчанию нет(Enter) " confirm
if [ "$confirm" == "y" ]; then
  echo
  echo "=== Отключение dhclient6 ==="
  systemctl stop dhclient6.service
  systemctl disable dhclient6.service
fi

#========================================================

echo
echo "=== Копирование проекта в каталог пользователя '$PWD' ==="
git clone https://github.com/Marat2010/manageBots
wait

cp -R manageBots/Scripts/.config/mc ~/.config/

#=======================================================

echo 
read -rp "=== Введите название проекта папки, если хотите поменять (manageBots - по умолчанию нет(Enter)): " proj_name

if [ -z "$proj_name" ]
then
    proj_name="manageBots"
    printf "\n=== Проект в папке: %s ===\n" "'$proj_name'"
else
    printf "\n=== Переносим проект 'manageBots' в -> %s \n" "'$proj_name'"
    mv -fv manageBots $proj_name
fi

cd $proj_name || { echo "----- !!!!! Ошибка !!!!! -----"; }
pwd
ls -al

#=======================================================
printf "\n\n=== Установка переменной окружения 'PROJECT_NAME' в ОС ===\n"
echo "PROJECT_NAME='$proj_name'" | sudo tee -a /etc/environment
#=======================================================

echo
echo "=== Установка вирт. окружения в папке $proj_name ==="
python3 -m venv .venv

echo
echo "=== Активация вирт.окружения ==="
source .venv/bin/activate

echo
echo "=== Установка из requirements.txt ==="
pip install --upgrade pip
pip install -r requirements.txt

echo
echo "=== Подготовка файлов окружения ==="
mv app/.env_example_manage app/.env_manage
mv our_Bots/bot_15001/.env_example_bot our_Bots/bot1/.env_bot
mv our_Bots/bot_15002/.env_example_bot our_Bots/bot2/.env_bot
echo
echo "====================================================="
echo "===   Отредактируйте переменные окружения:        ==="
echo "=== Для приложения файл: app/.env_manage          ==="
echo "=== Для первого бота:  our_Bots/bot1/.env_bot     ==="
echo "=== Для второго бота:  our_Bots/bot2/.env_bot     ==="
echo "====================================================="
read -rp "=== Если прочитали, для продолжения нажмите enter ==="

#=======================================================
printf "\n=== Предварительная подготовка Nginx конфигурации ===\n"
public_ip="$(wget -q -O - ipinfo.io/ip)"

read -rp "=== Введите IP адрес сервера VPS:($public_ip - по умолчанию (Enter))" set_ip

if [ -n "$set_ip" ]; then
    public_ip=$set_ip
fi
echo "PUBLIC_IP='$public_ip'" | sudo tee -a /etc/environment

./Scripts/nginx.sh "$public_ip"
./Scripts/ssl.sh "$public_ip"

#=======================================================

printf "\n\n=== Запуск сервиса, службы (SYSTEMD) Менеджер ботов ===\n"
read -rp "=== Запустить Менеджер ботов (manageBots) как службу? [y/N]: " run_service

if [ "$run_service" == "y" ]; then
    echo "
    [Unit]
    Description=Manage Bots service
    After=multi-user.target
     
    [Service]
    WorkingDirectory=$HOME/$proj_name/
    User=root
    Group=root
    Type=idle
    Restart=on-failure

    EnvironmentFile=/etc/environment
    Environment='PROJECT_NAME=manageBots'

    #ExecStart=/bin/bash -c 'cd $HOME/$proj_name && source .venv/bin/activate && /.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload'

    ExecStart=$HOME/$proj_name/Run_manage.sh

    [Install]
    WantedBy=multi-user.target
    " > "$HOME/$proj_name/ManageBots.service"

    sudo cp "$HOME/$proj_name/ManageBots.service" /lib/systemd/system/ManageBots.service
    sudo systemctl daemon-reload
    sudo systemctl enable ManageBots.service
    sudo systemctl start ManageBots.service
fi

printf "\n\n====== Информация для проверки =========================\n"
public_ip="$(wget -q -O - ipinfo.io/ip)"

printf "\n=== Test веба: https://%s:8443/test ===  \n" "$public_ip"
printf "\n=== API - Менеджер ботов (swagger): http://%s:12000/docs ===  \n" "$public_ip"
printf "\n=== Проверка токена: https://api.telegram.org/bot661....:AA...JQ/getWebhookInfo ===  \n"
printf "\n==========================================================\n"


#=======================================================
#=======================================================
#=======================================================
#ls -al | grep $proj_name
#=======================================================
#  sed 's/# autologin=dgod/autologin=ubuntu/' /path/to/file
#  sed 's/root/# root/' /etc/ftpusers
#=======================================================
#sudo cp $HOME/$PROJECT_NAME/ManageBots.service /lib/systemd/system/ManageBots.service
#sudo systemctl daemon-reload
#sudo systemctl enable ManageBots.service
#sudo systemctl start ManageBots.service
#=======================================================
#echo
#echo "=== Подготовка самоподписанных SSL сертификатов для IP  ===" 
#sudo mkdir /etc/ssl/nginx
#mkdir ~/SSL
#
#echo
#read -p "=== Введите IP адрес сервера VPS: " domain_ip
#
#openssl req -newkey rsa:2048 -sha256 -nodes -keyout $domain_ip.self.key -x509 -days 365 -out $domain_ip.self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Home/CN=$domain_ip"
#
#sudo mv $domain_ip.self.key /etc/ssl/nginx/
#sudo mv $domain_ip.self.crt /etc/ssl/nginx/

#=======================================================
#pip install aiogram==3.10.0
#pip freeze > requirements.txt
#=======================================================







