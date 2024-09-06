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
  openssl req -newkey rsa:2048 -sha256 -nodes -keyout /etc/ssl/nginx/"$1".self.key -x509 -days 365 -out /etc/ssl/nginx/"$1".self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Mara/CN='$1'"
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

openssl x509 -inform der -in YOURDER.der -out YOURPEM.pem

#============= IF ===================================
##if [ ! -d "/etc/ssl/nginx" ]; then
#  printf "\n=== Создаем директорию для SSL сертификатов Nginx ===\n"
#  sudo mkdir -pv /etc/ssl/nginx
#  sudo chown -v "$USER" /etc/ssl/nginx
##fi
#
##if [ ! -f "/etc/ssl/nginx/$1.self.crt" ]; then
#  printf "\n=== Формируем самоподписанные сертификаты и ключи ===\n"
#  openssl req -newkey rsa:2048 -sha256 -nodes -keyout /etc/ssl/nginx/"$1".self.key -x509 -days 365 -out /etc/ssl/nginx/"$1".self.crt -subj "/C=RU/ST=RT/L=KAZAN/O=Mara/CN='$1'"
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


