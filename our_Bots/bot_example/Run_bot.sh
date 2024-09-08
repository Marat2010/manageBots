#!/bin/bash

#=========================================
#Запуск бота:
#=========================================

cd "$HOME/$PROJECT_NAME" || { echo "----- !!!!! Ошибка !!!!! -----"; }
source .venv/bin/activate

python ./our_Bots/bot_15001/main.py 


#=========================================
#echo "=== Запуск сервиса, службы (SYSTEMD) бота ===" 
#echo
#sudo cp /$HOME/$PROJECT_NAME/our_Bots/bot1/bot_1.service /lib/systemd/system/bot_1.service
#sudo systemctl daemon-reload
#sudo systemctl enable bot_1.service
#sudo systemctl start bot_1.service
#=========================================
#cd /home/marat/PycharmProjects/manageBots/
#=========================================

