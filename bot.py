import logging
import os
from pyrogram import Client, filters
from plugins.config import Config

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


class Bot(Client):

    def __init__(self):
        super().__init__(
            "UploaderBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        print(f"New session started for {me.first_name} ({me.username})")

    async def stop(self):
        await super().stop()
        print("Session stopped. Bye!!")

app = Bot()
app.run()
