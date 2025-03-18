from aiogram import Router, types
from aiogram.filters import Command

ping_router = Router()

@ping_router.message(Command('ping'))
async def handle_ping(msg: types.Message):
    await msg.answer('pong')