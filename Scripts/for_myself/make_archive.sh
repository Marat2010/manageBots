#!/bin/bash

printf "===============================\n"
printf "=== Создание архива проекта ===\n"
printf "===============================\n\n"

cd ~/PycharmProjects || { echo " !!! Не могу перейти в каталог !!!"; exit 1;}

#if [ "$USER" != 'root' ] && [ "$USER" != 'marat' ]; then
if ! [ -d ~/PycharmProjects/"$1" ] || [ -z "$1" ]; then
  echo '=== Нет папки для архивирования!!! ==='
  read -rp "=== Сделать архив для 'manageBots'? [y/N]: " yes
  if [ "$yes" == "y" ]; then
    proj="manageBots"
  else
    exit 1
  fi
else
  proj=$1  # папка проекта
fi

date_arh="$(date +%d-%m-%Y_%T)"

tar -zcvf .My_Archive/"$proj"_"$date_arh".tar.gz -X ./.My_Archive/Script/exclude_archive.txt "$proj"

echo
echo "=== Архив здесь: <$HOME/PycharmProjects/.My_Archive/${proj}_${date_arh}.tar.gz>"
echo


#============================================
#============================================
