#!/usr/bin/zsh
rm ../app/slackbot.zip
cd ../.venv/lib/python3.9/site-packages
zip -r slackbot.zip .
mv slackbot.zip ../../../../app/slackbot.zip
cd ../../../../app
zip -g slackbot.zip bot.py
cd ../iac