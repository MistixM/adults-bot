# Import dependencies
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

# App
from app.handlers import routers
from app.utils.restore import restore_progress

import configparser
import asyncio
import logging

config = configparser.ConfigParser()
config.read('app/constants/config.ini')

# Enable logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename='debug.log'
)

# Init bot
bot = Bot(token=config['Main']['TELEGRAM_BOT_API'], 
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
dp.include_routers(*routers)


# Launch the bot
# Restore previous progress.
async def main():
    await restore_progress(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Bot started!")
    asyncio.run(main())
    print("Bot stopped!")