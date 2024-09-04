#!/bin/bash

# Предварительная подготовка Nginx конфигурации
# Запуск в шеле: ./Scripts/nginx_prepare.sh 178.1.1.1
# Первый параметр $1 - public_ip, внешний IP адрес (пример 178.1.1.1)

if [ "$USER" != "root" ]; then
  sudo chown -Rv "$USER" /etc/nginx/conf.d
fi

if [ ! -d "/etc/nginx/conf.d/bots" ]; then
  printf "\n Создаем директорию '/etc/nginx/conf.d/bots',\n где будем хранить конфигурации переадресации для управляемых нами ботов\n"
  mkdir -pv /etc/nginx/conf.d/bots
fi

printf "\n=== Формируем общую конфигурацию '/etc/nginx/conf.d/manageBots.conf' ===\n"

if [ ! -f "/etc/nginx/conf.d/manageBots.conf" ]; then
  echo "
  server {
    server_name $1;
    listen 8443 ssl;

    ssl_certificate       /etc/ssl/nginx/$1.self.crt;
    ssl_certificate_key   /etc/ssl/nginx/$1.self.key;

    error_log /var/log/nginx/manageBots.log;
    access_log /var/log/nginx/manageBots.log;

    location /test {
      charset UTF-8;
      add_header Content-Type text/html;
      return 200 '<!DOCTYPE html><meta charset=\'utf-8\'>
        <hr><h2>Менеджер ботов (проверка Nginx):</h2>
        <h3>&emsp;<i>Основная конфигурация:</i> /etc/nginx/conf.d/manageBots.conf<br><br>
        &emsp;<i>Конфигурация ботов:</i> /etc/nginx/conf.d/bots/...</h3><hr>';
    }

    include /etc/nginx/conf.d/bots/*.conf;
  }
  " > /etc/nginx/conf.d/manageBots.conf

  printf "=== Файл конфигурации Nginx создан! ===\n"

  printf "\n=== Перечитываем конфигурацию Nginx (Мягкий перезапуск) ===\n"
  sudo nginx -s reload
  sudo nginx -t

else
  printf "\n=== Файл конфигурации уже существует!!! ===\n"
  printf "=== Изменения НЕ внесены!!! ===\n"
  printf "=== Для изменений удалите или переименуйте файл 'manageBots.conf'!!! ===\n"
fi


#==========================================
#==========================================
#==========================================
#  printf "\n=== Перезапускаем Nginx сервер ===\n"
#  sudo systemctl daemon-reload
#  sudo systemctl restart nginx.service
#  systemctl status nginx.service
#==========================================
#     <p>This is a &nbsp; regular space.</p>
#    <p>This is a &ensp; two spaces gap.</p>
#    <p>This is a &emsp; four spaces gap.</p>
#==========================================
#if [ ! -f "/etc/nginx/conf.d/manageBots.conf" ]; then

#fi
#==========================================
#      charset UTF-8;
#        add_header charset utf-8;
#        return 200 '<!DOCTYPE html><meta charset=\'utf-8\'><h2> Проверка Nginx (менеджер ботов)!</h2>';
#==========================================
#        return 200 'TEST';
#        return 200 '== Проверка менеджера ботов! == <h1>TEST</h1> ';
#        add_header Content-Type text/plain;
#        default_type text/html;
#        return 200 '<!DOCTYPE html><h2>Проверка менеджера ботов!</h2>';
#        return 200 '<!DOCTYPE html><meta charset=\'utf-8\'><h2>Проверка менеджера ботов!</h2>';
#        charset utf-8;
#        source_charset utf-8;
#==========================================
#  sudo chown -Rv "$USER" /etc/nginx/conf.d
#  sudo chown -v "$USER" /etc/nginx/conf.d/bots
#==========================================
#touch /etc/nginx/conf.d/manageBots.conf
#fi

#  echo "dsdsd" > /etc/nginx/conf.d/11.txt
#==========================================
#echo "=== Перезапуск Nginx ==="
#sudo systemctl daemon-reload
#sudo systemctl restart nginx.service
#==============
#public_ip


