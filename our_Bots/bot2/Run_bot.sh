#!/bin/bash

#=========================================
#Запуск бота:
#=========================================


cd /home/marat/PycharmProjects/manageBots/
source .venv/bin/activate

#python ./our_Bots/bot2/bot_2.py
python ./our_Bots/bot2/config_bots.py


#=========================================
#echo "=== Запуск сервиса, службы (SYSTEMD) бота ===" 
#echo
#sudo cp /$HOME/$PROJECT_NAME/our_Bots/bot1/bot_2.service /lib/systemd/system/bot_2.service
#sudo systemctl daemon-reload
#sudo systemctl enable bot_2.service
#sudo systemctl start bot_2.service
#=========================================


