#!/bin/bash

#==============================================================
# ===== Удаление подготовленных каталогов сервера VPS =====
#==============================================================

echo "=== !!! Выполнять под пользователем root !!! ==="

if [ "$USER" != 'root' ] && [ "$USER" != 'marat' ]; then
    echo "=== Вы пользователь '$USER', необходимо запустить под пользователем: 'root'!"
    exit 1
fi

if [ "$PWD" == "$HOME/PycharmProjects/manageBots" ]; then
    echo "Вы в каталоге разработки, перейдите в домашнюю папку!!!"
    exit 1
fi

#======== Удаление папки проекта =============
rm -rfv "$PROJECT_NAME"

#=========== Остановка сервиса ===============
sudo systemctl disable ManageBots.service
sudo rm -fv /lib/systemd/system/ManageBots.service

#============ Остановка ботов ================
#sudo systemctl disable bot_*
sudo rm -fv /lib/systemd/system/bot_*

#========= Удаление настроек Nginx =============
sudo rm -fv /etc/nginx/conf.d/manageBots.conf
sudo rm -fv /etc/nginx/conf.d/api_manageBots.conf
sudo rm -rfv /etc/nginx/conf.d/bots

#========= Удаление сертификатов Nginx =============
sudo rm -rfv /etc/ssl/nginx
sudo rm -rfv SSL

#===================================================


