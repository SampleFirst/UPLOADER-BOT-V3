import os
import time
import psutil
import shutil
import string
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.config import Config
from plugins.translation import Translation
from plugins.database.add import add_user_to_database
from functions.forcesub import handle_force_subscribe

@Client.on_message(filters.command(["start"]) & filters.private)
async def start(client, message):
    try:
        if not message.from_user:
            return await message.reply_text("I don't know about you, sir.")
        
        await add_user_to_database(client, message)
        
        await client.send_message(
            Config.LOG_CHANNEL,
            f"#NEW_USER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{Config.BOT_USERNAME} !!"
        )
        
        if Config.UPDATES_CHANNEL:
            fsub = await handle_force_subscribe(client, message)
            if fsub == 400:
                return
        
        await message.reply_text(
            text=Translation.START_TEXT.format(message.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=Translation.START_BUTTONS
        )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
