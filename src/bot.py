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
from revChatGPT.Official import Prompt

chatbot = responses.chatbot

class aclient(AsyncTeleBot, StatesGroup):
    getChatReply = State()
    
    def __init__(self, TOKEN) -> None:
        super().__init__(TOKEN, state_storage=StateMemoryStorage())
        self.logger = telebot.logger
        telebot.logger.setLevel(logging.DEBUG)
        
async def split_message(text, chat_id, client, msg_id = None, code_block = False, is_start = -1):
    splitted_text = util.smart_split(text, chars_per_string=3000)        
    if code_block:
        for msg in splitted_text:
            print(msg)
            await client.send_message(chat_id, "```" + msg + "```", parse_mode = "markdown")
    else: 
        if is_start == 0:
            await client.edit_message_text(chat_id=chat_id, text=splitted_text[0], message_id=msg_id)
            if len(splitted_text) > 1:
                for msg in splitted_text[1:]:
                    await client.send_message(chat_id, msg)
        else:
            for msg in splitted_text:
                await client.send_message(chat_id, msg)

async def send_message(message, client, followup = False):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if user_id in chatbot.conversations.conversations:
        chatbot.load_conversation(user_id)
    try:
        if followup:
            question = message.text
        else:
            question = message.text.split("/chat ", 1)[1]
        response = emoji.emojize(f'{str(message.from_user.username)}:\t:outbox_tray:{question}\n\n:inbox_tray:')
        msg = await client.send_message(chat_id, response + "ChatGPT is thinking...", parse_mode = "markdown")
        response += "\n".join(f"{await responses.handle_response(question)}".split("\n\n"))
        if "```" in response:
            # Split the response if the code block exists
            parts = response.split("```")
            code_flag = 0
            for part in parts:
                if not(code_flag % 2):
                    await split_message(part, chat_id, client, msg.message_id, is_start = code_flag)
                else:
                    await split_message(part, chat_id, client, code_block = True)
                code_flag += 1
        else:
            await split_message(response, chat_id, client, msg.message_id, is_start = 0)
    except Exception as e:
        await client.send_message(message.chat.id, emoji.emojize(":red_exclamation_mark:**Error: Something went wrong, please try again!:red_exclamation_mark:**"), parse_mode = "markdown")
        client.logger.exception(f"Error while sending message: {e}")
    try:
        chatbot.save_conversation(user_id)
    except:
        await client.send_message(message.chat.id, emoji.emojize(":red_exclamation_mark:**Sorry I failed to save your conversation, please try again!:red_exclamation_mark:**"), parse_mode = "markdown")
    chatbot.prompt = Prompt()

def run_tele_bot():
    
    BOT_TOKEN = TOKEN
    client = aclient(BOT_TOKEN)

    @client.message_handler(commands=['chat'])
    async def chat(message: str, bypass = False):
        if message.text.split("/chat")[1] in ['', ' ']:
            await client.set_state(message.from_user.id, aclient.getChatReply, message.chat.id)
            await client.send_message(message.chat.id, emoji.emojize(':keyboard:Please enter a message to ask ChatGPT:'))
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
    
    @client.message_handler(commands=['reset'])
    async def reset(message):
        try:
            chatbot.remove_conversation(message.from_user.id)
            await client.reply_to(message, emoji.emojize(f":robot:**Info: I have forgotten everything from you {message.from_user.username}.**"), parse_mode = "markdown")
        except:
            await client.reply_to(message, emoji.emojize(f":red_exclamation_mark::robot:**Sorry I might not have correctly deleted your message history {message.from_user.username}.:red_exclamation_mark:**"), parse_mode = "markdown")
        

    @client.message_handler(commands=['start'])
    async def start_message(message):
        start_msg = emoji.emojize(f':robot: Welcome to ChatGPT-Tele! \n To begin chatting, type `/chat [message]` \n For more information, type `/help` \n To reset your conversation history, type `/reset` \n For complete documentation, please visit https://github.com/markusyeo/chatGPT-Tele-Bot')
        await client.reply_to(message, start_msg, parse_mode = "markdown")


    client.add_custom_filter(asyncio_filters.StateFilter(client))
    asyncio.run(client.infinity_polling())

