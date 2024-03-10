import logging
import asyncio
import json
import time
from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from functions.forcesub import handle_force_subscribe
from functions.display_progress import humanbytes
from plugins.database.add import add_user_to_database
from plugins.translation import Translation

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


@Client.on_message(filters.private & filters.regex(pattern=".*http.*"))
async def echo(bot, update):
    if not update.from_user:
        return await update.reply_text("I don't know about you sar :(")
    
    # Add user to database
    await add_user_to_database(bot, update)

    # Handle force subscribe
    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, update)
        if fsub == 400:
            return

    url = update.text

    # Check if the URL contains custom parameters
    if "|" in url:
        url_parts = url.split("|")
        if len(url_parts) >= 2:
            url = url_parts[0].strip()
    
    # Construct command to execute
    command_to_exec = [
        "yt-dlp",
        "--no-warnings",
        "--youtube-skip-dash-manifest",
        "-j",
        url
    ]
    
    logger.info(command_to_exec)

    # Send processing message
    chk = await bot.send_message(
        chat_id=update.chat.id,
        text=f'<b>Processing... ⏳</b>',
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )
    
    # Execute the command
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    
    # Handle error response
    if e_response and "nonnumeric port" not in e_response:
        error_message = e_response.replace("please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output.", "")
        if "This video is only available for registered users." in error_message:
            error_message += Translation.SET_CUSTOM_USERNAME_PASSWORD
        
        await chk.delete()
        time.sleep(3)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NO_VOID_FORMAT_FOUND.format(str(error_message)),
            reply_to_message_id=update.message_id,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        return False

    # Handle successful response
    if t_response:
        response_json = json.loads(t_response)
        randem = random_char(5)
        save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
            "/" + str(update.from_user.id) + f'{randem}' + ".json"
        with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
            json.dump(response_json, outfile, ensure_ascii=False)
        inline_keyboard = []
        duration = response_json.get("duration")

        if "formats" in response_json:
            for formats in response_json["formats"]:
                format_id = formats.get("format_id")
                format_string = formats.get("format_note", formats.get("format"))
                format_ext = formats.get("ext")
                approx_file_size = humanbytes(formats.get("filesize", ""))
                
                cb_string_video = "{}|{}|{}|{}".format(
                    "video", format_id, format_ext, randem)
                cb_string_file = "{}|{}|{}|{}".format(
                    "file", format_id, format_ext, randem)

                if "audio only" not in format_string:
                    ikeyboard = [
                        InlineKeyboardButton(
                            "🎬 " + format_string + " " + format_ext + " " + approx_file_size + " ",
                            callback_data=cb_string_video.encode("UTF-8")
                        )
                    ]
                    inline_keyboard.append(ikeyboard)

            if duration is not None:
                cb_string_64 = "{}|{}|{}|{}".format("audio", "64k", "mp3", randem)
                cb_string_128 = "{}|{}|{}|{}".format("audio", "128k", "mp3", randem)
                cb_string = "{}|{}|{}|{}".format("audio", "320k", "mp3", randem)
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎵 ᴍᴘ𝟹 " + "(" + "64 ᴋʙᴘs" + ")", callback_data=cb_string_64.encode("UTF-8")),
                    InlineKeyboardButton(
                        "🎵 ᴍᴘ𝟹 " + "(" + "128 ᴋʙᴘs" + ")", callback_data=cb_string_128.encode("UTF-8"))
                ])
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "🎵 ᴍᴘ𝟹 " + "(" + "320 ᴋʙᴘs" + ")", callback_data=cb_string.encode("UTF-8"))
                ])
                inline_keyboard.append([                 
                    InlineKeyboardButton(
                        "🔒 Close", callback_data='close')               
                ])
        else:
            format_id = response_json["format_id"]
            format_ext = response_json["ext"]
            cb_string_file = "{}|{}|{}|{}".format(
                "file", format_id, format_ext, randem)
            cb_string_video = "{}|{}|{}|{}".format(
                "video", format_id, format_ext, randem)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "🎬 sᴍᴇᴅɪᴀ",
                    callback_data=cb_string_video.encode("UTF-8")
                )
            ])
            cb_string_file = "{}={}={}".format(
                "file", format_id, format_ext)
            cb_string_video = "{}={}={}".format(
                "video", format_id, format_ext)
            inline_keyboard.append([
                InlineKeyboardButton(
                    "🎥 ᴠɪᴅᴇᴏ",
                    callback_data=cb_string_video.encode("UTF-8")
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await chk.delete()
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=update.message_id
        )
