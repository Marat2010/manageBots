#!/bin/bash

# Подготовка ssl сертификатов
# Запуск в шеле: ./Scripts/ssl.sh 178.1.1.1
# Первый параметр $1 - public_ip, внешний IP адрес (178.1.1.1)


#if [ ! -d "/etc/ssl/nginx" ]; then
  printf "\n=== Создаем директорию для SSL сертификатов Nginx ===\n"
  sudo mkdir -pv /etc/ssl/nginx  # пересоздаст, если есть
  sudo chown -v "$USER" /etc/ssl/nginx
#fi

#if [ ! -f "/etc/ssl/nginx/$1.self.crt" ]; then
  printf "\n=== Формируем самоподписанные сертификаты и ключи ===\n"
#  openssl genrsa -out webhook_pkey.pem 2048
  openssl genrsa -out /etc/ssl/nginx/"$1".self.key 2048
  openssl req -x509 -days 730 -newkey rsa:2048 -sha256 -nodes -keyout /etc/ssl/nginx/"$1".self.key -out /etc/ssl/nginx/"$1".self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=SUBota/OU='IT'/CN='$1'/emailAddress='smg_2006@list.ru'"
#fi

#==========================
#if [ ! -d "./SSL" ]; then
  printf "\n=== Создаем директорию './SSL' для линков сертификата. ===\n"
  mkdir -pv ./SSL
#fi

#==========================
#if [ ! -L "./SSL/$1.self.crt" ]; then
  printf "\n=== Создаем ссылку на сертификат SSL: ===\n"
  ln -svf /etc/ssl/nginx/"$1".self.crt ./SSL/"$1".self.crt  # пересоздаст, если есть
#fi

#if [ ! -L "./SSL/$1.self.key" ]; then
  printf "\n=== Создаем ссылку на ключ SSL: ===\n"
  ln -svf /etc/ssl/nginx/"$1".self.key ./SSL/"$1".self.key
#fi

#printf "\n============== END ===================\n"

#================================================
#================================================
#================================================
#    "last_error_message": "SSL error {error:0A000086:SSL routines::certificate verify failed}",

#openssl genrsa -out webhook_pkey.pem 2048
#openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#--------- 1 -----------
#openssl genrsa -out 178.204.149.172.self.key 2048
#openssl req -new -x509 -newkey rsa:2048 -sha256 -nodes -keyout /etc/ssl/nginx/178.204.149.172.self.key -x509 -days 365 -out /etc/ssl/nginx/178.204.149.172.self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Mara/OU='IT'/CN='$1'/emailAddress='smg_2006@list.ru'"

#------------------
#openssl x509 -inform der -in YOURDER.der -out YOURPEM.pem
#================================================
#================================================
#================================================
#openssl req -newkey rsa:2048 -sha256 -nodes -keyout /etc/ssl/nginx/176.124.209.65.self.key -x509 -days 365 -out /etc/ssl/nginx/176.124.209.65.self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Mara/CN='176.124.209.65'"
#============= IF ===================================

##if [ ! -d "/etc/ssl/nginx" ]; then
#  printf "\n=== Создаем директорию для SSL сертификатов Nginx ===\n"
#  sudo mkdir -pv /etc/ssl/nginx
#  sudo chown -v "$USER" /etc/ssl/nginx
##fi
#
##if [ ! -f "/etc/ssl/nginx/$1.self.crt" ]; then
#  printf "\n=== Формируем самоподписанные сертификаты и ключи ===\n"
#  openssl req -newkey rsa:2048 -sha256 -nodes -keyout /etc/ssl/nginx/"$1".self.key -x509 -days 365 -out /etc/ssl/nginx/"$1".self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Mara/CN='222.1'/emailAddress='smg_2006@list.ru'"
##fi
#
##==========================
##if [ ! -d "./SSL" ]; then
#  printf "\n=== Создаем директорию './SSL' для линков сертификата. ===\n"
#  mkdir -pv ./SSL
##fi
#
##==========================
##if [ ! -L "./SSL/$1.self.crt" ]; then
#  printf "\n=== Создаем ссылку на сертификат SSL: ===\n"
#  ln -svf /etc/ssl/nginx/"$1".self.crt ./SSL/"$1".self.crt
##fi
#
##if [ ! -L "./SSL/$1.self.key" ]; then
#  printf "\n=== Создаем ссылку на ключ SSL: ===\n"
#  ln -svf /etc/ssl/nginx/"$1".self.key ./SSL/"$1".self.key
##fi
#================================================
#  sudo mkdir -pv /etc/ssl/nginx
#==========================
#if [ ! -f "/etc/ssl/nginx/$1.self.crt" ]; then
#  echo "Переносим сертификат в '/etc/ssl/nginx'."
#  mv -f ./"$1".self.crt /etc/ssl/nginx/
#fi
#
#if [ ! -f "/etc/ssl/nginx/$1.self.key" ]; then
#  echo "Переносим ключ в '/etc/ssl/nginx'."
#  mv -f ./"$1".self.key /etc/ssl/nginx/
#fi
#===============================================================
#==============================================================
#if [ -e $HOME ] - объект
#if [ ! -d "/etc/ssl/nginx" ] - директория
#if [ -f $HOME ] - файл
#------
#if [ -s $file ] - пустой файл
#then
#echo "Файл $file содержит данные."
#else
#echo "Файл $file пустой."
#fi
#------
#  if [ -L "$LINK_OR_DIR" ]; then - символическая ссылка
#    # It is a symlink!
#    # Symbolic link specific commands go here.
#-------------------------
#mv ./SSL/$1.self.* ./etc_ssl/nginx/
#----------------------------------------
#openssl req -newkey rsa:2048 -sha256 -nodes -keyout $public_ip.self.key -x509 -days 365 -out $public_ip.self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Home/CN=$public_ip"
#sudo ln -s /etc/ssl/nginx/$domain_name.key ~/SSL/$domain_name.key
#sudo ln -s /etc/ssl/nginx/$domain_name.crt ~/SSL/$domain_name.crt
#===========================================
#вы можете использовать «-a» для and и «-o» для or. Пример:
#if [ $foo -ge 3 -a $foo -lt 10 ]; then
#===========================================
#mkdir -pv ./SSL

#mv ./$1.self.crt /etc/ssl/nginx/
#mv ./$1.self.key /etc/ssl/nginx/
#==========================================


