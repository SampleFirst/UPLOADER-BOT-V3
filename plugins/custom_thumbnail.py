import logging
import os
import random
import shutil
import string
from asyncio import TimeoutError
import asyncio
from asyncio import TimeoutError
from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery, ForceReply
from plugins.config import Config
from plugins.database.add import add_user_to_database
from plugins.database.database import db
from functions.forcesub import handle_force_subscribe
from plugins.settings.settings import *
from plugins.translation import Translation
from functions.help_Nekmo_ffmpeg import take_screen_shot
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
import psutil

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_message(filters.private & filters.photo)
async def photo_handler(client: Client, message: Message):
    if not message.from_user:
        return await message.reply_text("I don't know about you, sir :(")
    await add_user_to_database(client, message)
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(client, message)
        if fsub == 400:
            return
    editable = await message.reply_text("**👀 Processing...**")
    await db.set_thumbnail(message.from_user.id, thumbnail=message.photo.file_id)
    await editable.edit("**✅ Custom thumbnail saved successfully!**")


@Client.on_message(filters.private & filters.command(["delthumb", "deletethumbnail"]))
async def delete_thumb_handler(client: Client, message: Message):
    if not message.from_user:
        return await message.reply_text("I don't know about you, sir :(")
    await add_user_to_database(client, message)
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(client, message)
        if fsub == 400:
            return

    await db.set_thumbnail(message.from_user.id, thumbnail=None)
    await message.reply_text(
        "**🗑️ Custom thumbnail deleted successfully!**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚙️ Configure Settings", callback_data="OpenSettings")
                ]
            ]
        )
    )


@Client.on_message(filters.private & filters.command("showthumb"))
async def viewthumbnail(client, message):
    if not message.from_user:
        return await message.reply_text("I don't know about you, sir :(")
    await add_user_to_database(client, message)
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(client, message)
        if fsub == 400:
            return
    thumbnail = await db.get_thumbnail(message.from_user.id)
    if thumbnail is not None:
        await client.send_photo(
            chat_id=message.chat.id,
            photo=thumbnail,
            caption="Your current saved thumbnail",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🗑️ Delete Thumbnail", callback_data="deleteThumbnail")
                    ]
                ]
            ),
            reply_to_message_id=message.message_id)
    else:
        await message.reply_text(text="No thumbnail found 🤒")


async def get_thumbnail(client, message, duration, download_directory):
    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(message.from_user.id) + ".jpg"
    db_thumbnail = await db.get_thumbnail(message.from_user.id)
    if db_thumbnail is not None:
        thumbnail = await client.download_media(message=db_thumbnail, file_name=thumb_image_path)
        Image.open(thumbnail).convert("RGB").save(thumbnail)
        img = Image.open(thumbnail)
        img.resize((100, 100))
        img.save(thumbnail, "JPEG")
    else:
        thumbnail = None

    return thumbnail


async def get_thumbnail_v2(client, message, duration, download_directory):
    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(message.from_user.id) + ".jpg"
    db_thumbnail = await db.get_thumbnail(message.from_user.id)
    if db_thumbnail is not None:
        thumbnail = await client.download_media(message=db_thumbnail, file_name=thumb_image_path)
    else:
        thumbnail = await take_screen_shot(download_directory, os.path.dirname(download_directory), random.randint(0, duration - 1))

    return thumbnail


async def extract_metadata01(download_directory):

    width = 0
    height = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if metadata.has("width"):
            width = metadata.get("width")
        if metadata.has("height"):
            height = metadata.get("height")

    return width, height, duration


async def extract_metadata02(download_directory):

    width = 0
    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if metadata.has("width"):
            width = metadata.get("width")

    return width, duration


async def extract_metadata03(download_directory):

    duration = 0
    metadata = extractMetadata(createParser(download_directory))
    if metadata is not None:
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds

    return duration
  
