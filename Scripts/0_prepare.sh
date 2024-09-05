#!/bin/bash

# === Скрипт для предварительной подготовки сервера VPS ===

echo "=== !!! Выполнять под пользователем root !!! ==="

if [ $USER != 'root' ]; then
    echo "=== Вы пользователь '$USER', необходимо запустить под пользователем: 'root'!"
    exit
fi


# ---- Установка пакетов --------

apt update
echo
echo "=== Установка FTP сервера ==="
echo "=== Инструкция: https://help.reg.ru/support/servery-vps/oblachnyye-servery/ustanovka-programmnogo-obespecheniya/kak-ustanovit-ftp-server-na-ubuntu ==="
apt -y install vsftpd
systemctl enable vsftpd

echo
echo "=== Установка Midnight Commander ==="
apt -y install mc
echo

echo
echo "=== Установка Lynx ==="
apt -y install lynx
echo

echo
echo "============================================================="
echo "=====      Установка sqlite3 для терминала              ====="
echo "=== # sqlite3 DB/mb.sqlite3 - подключение к БД            ==="
echo "=== sqlite> select * from bots; - просмотр таблицы 'bots' ==="
echo "============================================================="
read -p "=====  Если прочитали, нажмите enter для продолжения ===== "
apt install sqlite3
echo

echo "=== Установка пакета Nginx ==="
sudo apt -y install nginx
sudo systemctl enable nginx

echo
echo "=== Установка модуля VENV (python3-venv) ==="
apt -y install python3-venv

echo
echo "=== FTP: Настройка сервера ==="
cp /etc/vsftpd.conf /etc/vsftpd.conf.original

echo "listen=YES" > /etc/vsftpd.conf
echo "listen_ipv6=NO" >> /etc/vsftpd.conf
echo "anonymous_enable=NO" >> /etc/vsftpd.conf
echo "local_enable=YES" >> /etc/vsftpd.conf
echo "write_enable=YES" >> /etc/vsftpd.conf
echo "local_umask=022" >> /etc/vsftpd.conf
echo "dirmessage_enable=YES" >> /etc/vsftpd.conf
echo "use_localtime=YES" >> /etc/vsftpd.conf
echo "xferlog_enable=YES" >> /etc/vsftpd.conf
echo "connect_from_port_20=YES" >> /etc/vsftpd.conf
echo "xferlog_file=/var/log/vsftpd.log" >> /etc/vsftpd.conf
echo "xferlog_std_format=YES" >> /etc/vsftpd.conf
echo "chroot_local_user=YES" >> /etc/vsftpd.conf
echo "allow_writeable_chroot=YES" >> /etc/vsftpd.conf
echo "local_root=/" >> /etc/vsftpd.conf
echo "pam_service_name=vsftpd" >> /etc/vsftpd.conf
echo "#userlist_enable=YES" >> /etc/vsftpd.conf
echo "userlist_file=/etc/vsftpd.userlist" >> /etc/vsftpd.conf
echo "#userlist_deny=NO" >> /etc/vsftpd.conf
echo "userlist_deny=YES" >> /etc/vsftpd.conf
echo "" >> /etc/vsftpd.conf

echo
echo "=== FTP: Формирование SSL-сертификата  ==="
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/vsftpd.pem -out /etc/ssl/private/vsftpd.pem -subj "/C=RU/ST=RT/L=KAZAN/O=Home/CN=1/emailAddress=em"

echo "rsa_cert_file=/etc/ssl/private/vsftpd.pem" >> /etc/vsftpd.conf
echo "rsa_private_key_file=/etc/ssl/private/vsftpd.pem" >> /etc/vsftpd.conf
echo "ssl_enable=YES" >> /etc/vsftpd.conf
echo "" >> /etc/vsftpd.conf

systemctl restart vsftpd
echo
echo "==========================================================================="
echo "==== Для доступа root-a по ftp закоментируйте его в файле /etc/ftpusers ==="
echo "====        И перезапустите: systemctl restart vsftpd                   ==="
echo "==========================================================================="
read  -p "=====    Если прочитали, для продолжения нажмите enter               ===== "

echo
echo "=== Отключение dhclient6 ==="
systemctl stop dhclient6.service
systemctl disable dhclient6.service

# ---- Смена пароля root-а --------

echo 
read -p "=== Сменить у пользователя 'root' пароль? [y/N]: " change_passwd_root

if [ "$change_passwd_root" == "y" ]
then
    passwd root
fi

#========================================================

echo
echo "=== Копирование проекта в каталог пользователя '$HOME' ==="
git clone https://github.com/Marat2010/manageBots
wait

#=======================================================

echo 
read -p "=== Введите название проекта, папки (manageBots): " proj_name

if [ -z $proj_name ]
then
    proj_name="manageBots"
fi

mkdir ~/$proj_name
cd ~/$proj_name

echo "PROJECT_NAME='$proj_name'" | sudo tee -a /etc/environment

echo
echo "=== Установка вирт. окружения в папке $proj_name ==="
python3 -m venv .venv

echo
echo "=== Активация вирт.окружения ==="
source venv/bin/activate

echo
echo "=== Установка из requirements.txt ==="
pip3 install --upgrade pip
pip install -r requirements.txt

echo
echo "=== Подготовка файлов окружения ==="
mv app/.env_example_manage app/.env_manage
mv our_Bots/bot1/.env_example_bot our_Bots/bot1/.env_bot
mv our_Bots/bot2/.env_example_bot our_Bots/bot2/.env_bot
echo
echo "====================================================="
echo "===   Отредактируйте переменные окружения:        ==="
echo "=== Для приложения файл: app/.env_manage          ==="
echo "=== Для первого бота:  our_Bots/bot1/.env_bot     ==="
echo "=== Для второго бота:  our_Bots/bot2/.env_bot     ==="
echo "====================================================="
read -p "=== Если прочитали, для продолжения нажмите enter ==="


echo "=== Запуск сервиса, службы (SYSTEMD) Менеджер ботов ===" 
echo 
read -p "=== Запустить Менеджер ботов (manageBots) как службу? [y/N]: " mb_service

if [ "$mb_service" == "y" ]
then
    sudo cp /$HOME/$PROJECT_NAME/ManageBots.service /lib/systemd/system/ManageBots.service
    sudo systemctl daemon-reload
    sudo systemctl enable ManageBots.service
    sudo systemctl start ManageBots.service
fi


#=======================================================
#=======================================================
#=======================================================
#sudo cp /$HOME/$PROJECT_NAME/ManageBots.service /lib/systemd/system/ManageBots.service
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







