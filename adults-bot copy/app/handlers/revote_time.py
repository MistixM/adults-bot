# Aiogram tools
from aiogram import Router, types
from aiogram.filters import Command
import asyncio

# DB and utils
from app.database.db import add_data, get_data
from app.utils.poll_closure import monitor_poll_closure

# Time
from datetime import datetime, timezone, timedelta

from app.constants.global_settings import REVOTE_POLL_CLOSE_TIME, RV_TIME_ERR, RV_TIME_QUESTION, RV_TIME_OPTIONS

revote_time_router = Router()

# Creates a poll for the time revote
@revote_time_router.message(Command('revote_time'))
async def handle_command(msg: types.Message) -> None:
    # Get chat info
    chat_id = msg.chat.id

    # Get group data from the DB
    group = get_data('groups', chat_id)

    # Important to check current group states
    if group.get('day') == 'pending' or group.get('time') == 'pending':
        await msg.answer(RV_TIME_ERR)
        return

    # Init closetime (48 hours by default)
    close_time = int((datetime.now(timezone.utc).now() + timedelta(hours=REVOTE_POLL_CLOSE_TIME)).timestamp())

    # Create a poll with question and options
    time_poll = await msg.bot.send_poll(chat_id=chat_id,
                                        question=RV_TIME_QUESTION,
                                        options=RV_TIME_OPTIONS,
                                        is_anonymous=True)

    # Add poll data to the DB
    add_data('polls', time_poll.poll.id,
             {"chat_id": chat_id,
              "message_id": time_poll.message_id,
              "title": "revote_time",
              "close_time": close_time})
    
    # Create an asynchronous task
    asyncio.create_task(monitor_poll_closure(msg.bot, chat_id,
                                             time_poll.message_id, time_poll.poll.id,
                                             close_time))