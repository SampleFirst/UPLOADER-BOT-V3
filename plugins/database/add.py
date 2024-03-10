from plugins.config import Config
from .database import db
from pyrogram import Client
from pyrogram.types import Message


async def add_user_to_database(bot: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        


