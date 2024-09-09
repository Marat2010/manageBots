#!/bin/bash

#=========================================
#Запуск приложения Менеджер ботов:
#=========================================

#cd $HOME/manageBots
cd "$HOME/$PROJECT_NAME" || { exit 1; }
source .venv/bin/activate

uvicorn app.main:app --host 127.0.0.1 --port 12000 --reload


#=========================================
#=========================================
#uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload
#=========================================
#echo "=== Запуск сервиса, службы (SYSTEMD) бота ==="
#echo
#sudo cp /$HOME/$PROJECT_NAME/ManageBots.service /lib/systemd/system/ManageBots.service
#sudo systemctl daemon-reload
#sudo systemctl enable Aiogram3_bot.service
#sudo systemctl start Aiogram3_bot.service
#=========================================
#echo 
#read -p "=== Введите название проекта (папки): " proj_name
#mkdir ~/$proj_name
#cd ~/$proj_name
#=========================================
#/home/marat/PycharmProjects/manageBots/.venv/bin/python /home/marat/PycharmProjects/manageBots/app/main.py 
#uvicorn app.main:app --host 0.0.0.0 --port 12000 --reload

