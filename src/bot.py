import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage
from telebot import asyncio_filters
import asyncio
from telebot import util
from src import responses
from env import TOKEN
import logging
import emoji

class aclient(AsyncTeleBot, StatesGroup):
    getChatReply = State()

    def __init__(self, TOKEN) -> None:
        super().__init__(TOKEN, state_storage=StateMemoryStorage())
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

async def send_message(message, client, followup = False):
    chat_id = message.chat.id        
    try:
        if followup:
            question = message.text
        else:
            question = message.text.split("/chat ", 1)[1]
        print("i am working")
        response = emoji.emojize(f'{str(message.from_user.username)}:\t:outbox_tray:{question}') + "\n"
        response += "\n".join(emoji.emojize(f"\n:inbox_tray:{await responses.handle_response(question)}").split("\n\n"))
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
    async def chat(message: str, bypass = False):
        if message.text.split("/chat")[1] in ['', ' ']:
            await client.set_state(message.from_user.id, aclient.getChatReply, message.chat.id)
            await client.send_message(message.chat.id, 'Please enter a message to ask GPT:')
        else:
            username = str(message.from_user.username)
            channel = str(message.sender_chat)
            client.logger.info(
                f"\x1b[31m{username}\x1b[0m : ({channel})")
            await send_message(message, client)

    @client.message_handler(state=aclient.getChatReply)
    async def chat_followup(message):
        username = str(message.from_user.username)
        channel = str(message.sender_chat)
        client.logger.info(
            f"\x1b[31m{username}\x1b[0m : ({channel})")
        await send_message(message, client, followup=True)
        await client.delete_state(message.from_user.id, message.chat.id)

    @client.message_handler(commands=['help'])
    async def help(message):
        await client.reply_to(message, emoji.emojize(":star:**BASIC COMMANDS** \n  `/chat [message]` Chat with ChatGPT!\n  For complete documentation, please visit https://github.com/markusyeo/chatGPT-Tele-Bot"), parse_mode = "markdown")
        client.logger.info(
            "\x1b[31mSomeone need help!\x1b[0m")

    @client.message_handler(commands=['start'])
    async def start_message(message: str):
        start_msg = emoji.emojize(f':robot: Welcome to ChatGPT-Tele! \n To begin chatting, type `/chat [message]` \n For more information, type `/help`')
        await client.reply_to(message, start_msg, parse_mode = "markdown")

    client.add_custom_filter(asyncio_filters.StateFilter(client))
    asyncio.run(client.infinity_polling())

