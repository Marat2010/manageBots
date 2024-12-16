#!/bin/bash
#=============================================================
# === Скрипт для установки внешнего (публичного) IP адреса ===
# ===           в переменные окружения                     ===
#=============================================================

public_ip="$(wget -q -O - ipinfo.io/ip)"

sudo sed -i "s/^PUBLIC_IP=.*/PUBLIC_IP='$public_ip'/g" /etc/environment

#=============================================================
# echo "PUBLIC_IP='$public_ip'" | sudo tee -a /etc/environment
#sudo sed -i 's/root/# root/' /etc/ftpusers
