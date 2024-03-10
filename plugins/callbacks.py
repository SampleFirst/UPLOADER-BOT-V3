import os
import logging

from pyrogram import Client, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from functions.display_progress import progress_for_pyrogram, humanbytes

from plugins.config import Config
from plugins.dl_button import ddl_call_back
from plugins.youtube_dl_button import youtube_dl_call_back
from plugins.settings.settings import OpenSettings
from plugins.translation import Translation
from plugins.database.database import db

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



@Client.on_callback_query()
async def button(client, query):
    if query.data == "home":
        await query.message.edit_text(
            text=Translation.START_TEXT.format(query.from_user.mention),
            reply_markup=Translation.START_BUTTONS,
            disable_web_page_preview=True
        )
    elif query.data == "help":
        await query.message.edit_text(
            text=Translation.HELP_TEXT,
            reply_markup=Translation.HELP_BUTTONS,
            disable_web_page_preview=True
        )
    elif query.data == "about":
        await query.message.edit_text(
            text=Translation.ABOUT_TEXT,
            reply_markup=Translation.ABOUT_BUTTONS,
            disable_web_page_preview=True
        )
    elif query.data == "OpenSettings":
        await query.answer()
        await OpenSettings(query.message)
    elif query.data == "showThumbnail":
        thumbnail = await db.get_thumbnail(query.from_user.id)
        if not thumbnail:
            await query.answer("You didn't set any custom thumbnail!", show_alert=True)
        else:
            await query.answer()
            await client.send_photo(
                query.message.chat.id, 
                thumbnail, "Custom Thumbnail",
                reply_markup=types.InlineKeyboardMarkup(
                    [
                        [
                            types.InlineKeyboardButton("Delete Thumbnail", callback_data="deleteThumbnail")
                        ]
                    ]
                )
            )
    elif query.data == "deleteThumbnail":
        await db.set_thumbnail(query.from_user.id, None)
        await query.answer("Okay, I deleted your custom thumbnail. Now I will apply default thumbnail.", show_alert=True)
        await query.message.delete(True)
    elif query.data == "setThumbnail":
        await query.message.edit_text(
            text=Translation.TEXT,
            reply_markup=Translation.BUTTONS,
            disable_web_page_preview=True
        )

    elif query.data == "triggerUploadMode":
        await query.answer()
        upload_as_doc = await db.get_upload_as_doc(query.from_user.id)
        if upload_as_doc:
            await db.set_upload_as_doc(query.from_user.id, False)
        else:
            await db.set_upload_as_doc(query.from_user.id, True)
        await OpenSettings(query.message)
    elif "close" in query.data:
        await query.message.delete(True)

    elif "|" in query.data:
        await youtube_dl_call_back(client, query)
    elif "=" in query.data:
        await ddl_call_back(client, query)

    else:
        await query.message.delete()
