#!/bin/bash

#=========================================
#Запуск бота:
#=========================================


cd /home/marat/PycharmProjects/manageBots/
source .venv/bin/activate

#python ./our_Bots/bot1/bot_1.py 
python ./our_Bots/bot1/config_bots.py


#=========================================
#echo "=== Запуск сервиса, службы (SYSTEMD) бота ===" 
#echo
#sudo cp /$HOME/$PROJECT_NAME/our_Bots/bot1/bot_1.service /lib/systemd/system/bot_1.service
#sudo systemctl daemon-reload
#sudo systemctl enable bot_1.service
#sudo systemctl start bot_1.service
#=========================================


