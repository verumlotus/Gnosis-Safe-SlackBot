# Gnosis-Safe-SlackBot
Slack Bot that will periodically fetch queued transactions in a Gnosis Safe and post them in Slack. 

## Background
[Gnosis Safe](https://gnosis-safe.io/) is the most commonly used multi-sig for treasury management, governance upgrades, and coordinated actions broadly. It's easy for time-sensitive transactions to be forgotten in the gnosis safe queue until it's too late to execute them. This repo contains a simple slack bot to ping a slack channel every X hours (X is configurable). 
 
 ## Setup Steps
 - Python package dependencies are handled using [poetry](https://python-poetry.org/). Run `poetry install` to install the necessary packages. 
 - Follow `.env.template` and fill out a `.env` file with the appropriate API keys and gnosis safe address
 - To obtain a slack webhook, refer to [this](https://api.slack.com/messaging/webhooks) guide

## Deployment
 `app/bot.py` is meant to be an AWS lambda cron job that is invoked after a certain amount of time has elapsed. You can refer to the `iac/main.tf` terraform file to deploy using the terraform CLI, but note that some of the code is specific to my machine/setup so modifications are required. You can alternatively zip your files manually and upload them to Lambda and set a time increment using the GUI (see [here](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html)).
 
 ## Disclaimer
 This bot was built for fun and personal utility – it hasn't been stress-tested so please don't rely on this solely to see when trasnactions to sign are in the queue!
