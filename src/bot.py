import telebot
from telebot.async_telebot import AsyncTeleBot
import asyncio
from telebot import util
from src import responses
from env import TOKEN
import logging

class aclient(AsyncTeleBot):
    def __init__(self, TOKEN) -> None:
        super().__init__(TOKEN)
        self.logger = telebot.logger
        telebot.logger.setLevel(logging.DEBUG)

async def split_message(text, chat_id, client, code_block = False):
    splitted_text = util.smart_split(text, chars_per_string=3000)
    if code_block:
        for msg in splitted_text:
            await client.send_message(chat_id, "```" + msg + "```", parse_mode = "markdown")
    else: 
        for msg in splitted_text:
            await client.send_message(chat_id, msg)

async def send_message(message, client):
    chat_id = message.chat.id
    try:
        response = f'{str(message.from_user.username)}:\t{message.text.split("/chat ")[1]}'
        question = message.text.split("/chat ")[1]
        response = f"{response}{await responses.handle_response(question)}"
        if "```" in response:
            # Split the response if the code block exists
            parts = response.split("```")
            code_flag = 0
            for part in parts:
                if not(code_flag % 2):
                    await split_message(part, chat_id, client)
                else:
                    await split_message(part, chat_id, client, True)
                code_flag += 1
        else:
            await split_message(response, chat_id, client)
    except Exception as e:
        await client.send_message(message.chat.id, "> **Error: Something went wrong, please try again later!**")
        client.logger.exception(f"Error while sending message: {e}")

def run_tele_bot():
    
    BOT_TOKEN = TOKEN
    client = aclient(BOT_TOKEN)

    @client.message_handler(commands=['chat'])
    async def chat(message: str):
        username = str(message.from_user.username)
        channel = str(message.sender_chat)
        client.logger.info(
            f"\x1b[31m{username}\x1b[0m : ({channel})")
        await send_message(message, client)

    @client.message_handler(commands=['help'])
    async def help(message):
        await client.reply_to(message, ":star:**BASIC COMMANDS** \n  `/chat [message]` Chat with ChatGPT!\n  For complete documentation, please visit https://github.com/markusyeo/chatGPT-Tele", parse_mode = "markdown")
        client.logger.info(
            "\x1b[31mSomeone need help!\x1b[0m")

    asyncio.run(client.polling())