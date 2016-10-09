#!/usr/bin/bash
filename=".gitignore"
while read -r line
do
  pattern="$line"
  echo -e "\e[39m-- Deleting files matching \e[4m\e[93m'$pattern'\e[24m\e[39m pattern. --\e[91m"
  rm -R $pattern
done < "$filename"