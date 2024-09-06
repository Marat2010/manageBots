#!/bin/bash


echo "=== Запуск сервиса, службы (SYSTEMD) для бота ==="

#=======================================================

read -rp "=== Выберите бота bot_1 или bot_2 ? [1/2]: " number
printf "Вы выбрали: %s" "$number"

#=======================================================

printf "\n\n=== Предварительно необходимо указать переменные окружения в ./our_Bots/bot$number/.env_bot ===\n"

read -rp "=== Запустить бота (bot_$number) как службу? [y/N]: " run_service

if [ "$run_service" == "y" ]; then
    echo "
    [Unit]
    Description=Aiogram3 bot_$number service
    After=multi-user.target
     
    [Service]
    User=root
    Group=root
    Type=idle
    Restart=on-failure

    EnvironmentFile=/etc/environment

    ExecStart=/bin/bash -c 'cd $HOME/$PROJECT_NAME && source .venv/bin/activate && ./our_Bots/bot$number/Run_bot.sh'

    [Install]
    WantedBy=multi-user.target
    " > "/$HOME/$PROJECT_NAME/our_Bots/bot$number/bot_$number.service"

    sudo cp "/$HOME/$PROJECT_NAME/our_Bots/bot$number/bot_$number.service" "/lib/systemd/system/bot_$number.service"

    sudo systemctl daemon-reload
    sudo systemctl enable bot_"$number".service
    sudo systemctl start bot_"$number".service
fi

