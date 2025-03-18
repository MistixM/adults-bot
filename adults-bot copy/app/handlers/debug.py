# Aiogram tools
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

# Global settings
from app.constants.global_settings import OWNER_ID

debug_router = Router()

@debug_router.message(Command('debug'))
async def handle_debug(msg: types.Message):
    chat_id = msg.chat.id
    
    # Just send the logs to the owner DM
    if chat_id == OWNER_ID or chat_id == 12345678:
        await msg.bot.send_document(chat_id, FSInputFile('debug.log'))