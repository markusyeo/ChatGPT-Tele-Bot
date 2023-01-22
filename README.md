# chatGPT-Tele-Bot

> ### This is a project that provides you to build your own Telegram bot using ChatGPT
An up to date Telegram Bot that generates replies using GPT-3. **Take note that this does not use ChatGPT at the moment so it does not have content retention.
---
> ### Thank you for Zero's [chatGPT-discord-bot](https://github.com/Zero6992/chatGPT-discord-bot) efforts in maintaining the discord bot. I want to give credit to Zero whose code I based this Telegram bot off on and influencing this readme. I'll be keeping this up to date as openai releases the new API and updating the features of the bot when there's an update.

## Features

* `/chat [message]` Chat with ChatGPT!
* `/help` Get help

# Setup

## Step 1: Set up env.py
1. **Change the file name of `env.py.example` to `env.py`**

## Step 2: Create a Telegram Bot
1. Create a Telegram bot using BotFather. Note down the provided bot API token.

2. Store the API Key to `env.py` under the `TOKEN`

## Step 3: Geanerate a OpenAI API key

1. Go to https://beta.openai.com/account/api-keys

2. Click Create new secret key

   ![image](https://user-images.githubusercontent.com/89479282/207970699-2e0cb671-8636-4e27-b1f3-b75d6db9b57e.PNG)

2. Store the SECRET KEY to `env.py` under the `OPENAI_KEY`

## Step 4: Build the docker file

1. Run the following command on Docker to build the Docker image.
```
docker build -t gpt-tele-bot .
```
2. Finally run a Docker container using the built image.

```
docker run --name <container_name> -d gpt-tele-bot
```

You may rename `<container_name>` as you wish.

# Alternatively

## Running the bot on your desktop

1. Follow Steps 1 to 3 above to set up your tokens
2. Navigate to the directory where you cloned the ChatGPT Telegram bot
3. Run `python3 -m pip install -r requirements.txt` to install the dependencies
4. Run `python3 main.py` to start the bot

### Have fun asking the bot questions!
