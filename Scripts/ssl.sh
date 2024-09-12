#!/bin/bash

# Подготовка ssl сертификатов
# Запуск в шеле: ./Scripts/ssl.sh 178.1.1.1
# Первый параметр $1 - public_ip, внешний IP адрес (178.1.1.1)


if [ ! -d "/etc/ssl/nginx" ]; then
  printf "\n=== Создаем директорию для SSL сертификатов Nginx ===\n"
  sudo mkdir -pv /etc/ssl/nginx  # пересоздаст, если есть
  sudo chown -v "$USER" /etc/ssl/nginx
fi

if [ ! -f "/etc/ssl/nginx/$1.self.crt" ]; then
  printf "\n=== Формируем самоподписанные сертификаты и ключи ===\n"
  sudo openssl genrsa -out /etc/ssl/nginx/"$1".self.key 2048
  sudo openssl req -new -x509 -days 3650 -subj "/C=RU/ST=RT/L=KAZAN/O=SUBota/OU=IT/CN=$1/emailAddress=smg_2006@list.ru" -key /etc/ssl/nginx/"$1".self.key -out /etc/ssl/nginx/"$1".self.crt
fi

#==========================
if [ ! -d "./SSL" ]; then
  printf "\n=== Создаем директорию './SSL' для линков сертификата. ===\n"
  mkdir -pv ./SSL
fi

#==========================
if [ ! -L "./SSL/$1.self.crt" ]; then
  printf "\n=== Создаем ссылку на сертификат SSL: ===\n"
  ln -svf /etc/ssl/nginx/"$1".self.crt ./SSL/"$1".self.crt  # пересоздаст, если есть
fi

if [ ! -L "./SSL/$1.self.key" ]; then
  printf "\n=== Создаем ссылку на ключ SSL: ===\n"
  ln -svf /etc/ssl/nginx/"$1".self.key ./SSL/"$1".self.key
fi


#================================================
#================================================
#    "last_error_message": "SSL error {error:0A000086:SSL routines::certificate verify failed}",

#openssl genrsa -out webhook_pkey.pem 2048
#openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem

#--------- 1 -----------
#openssl genrsa -out 178.204.149.172.self.key 2048
#openssl req -new -x509 -newkey rsa:2048 -sha256 -nodes -keyout /etc/ssl/nginx/178.204.149.172.self.key -x509 -days 365 -out /etc/ssl/nginx/178.204.149.172.self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Mara/OU='IT'/CN='$1'/emailAddress='smg_2006@list.ru'"

#openssl req -newkey rsa:2048 -sha256 -nodes -keyout /etc/ssl/nginx/176.124.209.65.self.key -x509 -days 365 -out /etc/ssl/nginx/176.124.209.65.self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Mara/CN='176.124.209.65'"
#================================================
#================================================





