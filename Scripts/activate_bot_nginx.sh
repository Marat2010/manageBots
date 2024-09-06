#!/bin/bash

# Добавления бота в Nginx конфигурацию
# Запуск в шелле: ./Scripts/activate_bot_nginx.sh "Yes" "/bot/" "66151xxxxx:AAHbuZTxxxxxxxxxxxxxxxxJqGJnJQ" ...
# Первый параметр $1 - (Yes, No) добавить или удалить, $2 - WEBHOOK_PATH (в примере "/bot/"),
# $3 - token_tg, токен ТГ (в примере 66151xxxxx:AAHbuZTxxxxxxxxxxxxxxxxJqGJnJQ)
# $4 - web_server_host, $5 - web_server_port

if [ "$USER" != "root" ]; then
    echo "Для выполнения скрипта нужны права sudo, права суперпользователя"
fi

if [ "$1" == "Yes" ]; then
  printf "\n=== Добавляем бота в конфигурации Nginx ===\n"
  echo "
      location $2$3 {
        proxy_set_header Host \$http_host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_redirect off;
        proxy_buffering off;
        proxy_pass https://$4:$5;
    }
  " > /etc/nginx/conf.d/bots/bot_"$3".conf  # bot_"$5".conf - Можно указать port, а не токен
  echo "=== Файл конфигурации бота: bot_$3.conf ==="
elif [ "$1" == "No" ]; then
  printf "\n=== Удаляем бота из конфигурации Nginx ===\n"
  rm -v /etc/nginx/conf.d/bots/bot_"$3".conf  # bot_"$5".conf - Можно указать port, а не токен
else
  printf "\n=== Неверное состояние бота (должно быть Yes или No) ===\n"
fi

printf "\n=== Перечитываем конфигурацию Nginx (Мягкий перезапуск) ===\n"
sudo nginx -s reload
#sudo nginx -t
sudo systemctl status nginx.service |head -n 3


#===================================
#===================================
#if [ ! -f "/etc/nginx/conf.d/bots/bot_$1.conf" ]; then
#fi
#===================================
#sudo nginx -s reload
#sudo systemctl reload nginx
#sudo nginx -t
#sudo systemctl status nginx.service
#sudo systemctl status nginx.service |head -n 3 |tail -n 1
