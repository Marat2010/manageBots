#!/bin/bash

# Предварительная подготовка Nginx конфигурации
# Запуск в шеле: ./Scripts/nginx_prepare.sh 178.1.1.1
# Первый параметр $1 - public_ip, внешний IP адрес (пример 178.1.1.1)

if [ "$USER" != "root" ]; then
  sudo chown -Rv "$USER" /etc/nginx/conf.d
fi

if [ ! -d "/etc/nginx/conf.d/bots" ]; then
  printf "\n Создаем директорию '/etc/nginx/conf.d/bots',\n где будем хранить конфигурации переадресации для управляемых нами ботов\n"
  sudo mkdir -pv /etc/nginx/conf.d/bots
fi

#=====================================================
printf "\n=== Формируем общую конфигурацию '/etc/nginx/conf.d/manageBots.conf' ===\n"

if [ ! -f "/etc/nginx/conf.d/manageBots.conf" ]; then
  echo "server {
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
  " | sudo tee /etc/nginx/conf.d/manageBots.conf

  printf "=== Файлы конфигурации Nginx создан (manageBots.conf)! ===\n"

else
  printf "\n=== Файл конфигурации уже существует!!! ===\n"
  printf "=== Изменения НЕ внесены!!! ===\n"
  printf "=== Для изменений удалите или переименуйте файлы 'manageBots.conf', 'api_manageBots.conf' !!! ===\n"
fi

#=====================================================
printf "\n=== Формируем конфигурацию для API '/etc/nginx/conf.d/api_manageBots.conf' ===\n"

if [ ! -f "/etc/nginx/conf.d/api_manageBots.conf" ]; then
  echo "server {
  server_name _;

  listen 5080 ssl;

  ssl_certificate       /etc/ssl/nginx/$1.self.crt;
  ssl_certificate_key   /etc/ssl/nginx/$1.self.key;

  error_log /var/log/nginx/manageBots.log;
  access_log /var/log/nginx/manageBots.log;

  location / {
    proxy_set_header Host \$http_host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_redirect off;
    proxy_buffering off;
    proxy_pass http://localhost:12000;
  }
}
  " | sudo tee /etc/nginx/conf.d/api_manageBots.conf
  printf "=== Файлы конфигурации Nginx создан (api_manageBots.conf)! ===\n"

else
  printf "\n=== Файл конфигурации уже существует!!! ===\n"
  printf "=== Изменения НЕ внесены!!! ===\n"
  printf "=== Для изменений удалите или переименуйте файл 'api_manageBots.conf' !!! ===\n"
fi

printf "\n=== Перечитываем конфигурацию Nginx (Мягкий перезапуск) ===\n"
sudo nginx -s reload
sudo nginx -t

#=====================================================


#==========================================
#==========================================
#==========================================
#  printf "\n=== Перезапускаем Nginx сервер ===\n"
#  sudo systemctl daemon-reload
#  sudo systemctl restart nginx.service
#  systemctl status nginx.service
#==========================================

