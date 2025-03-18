# Aiogram tools
from aiogram import Router, types
from aiogram.filters import Command
import asyncio

# DB and utils
from app.database.db import get_data, add_data
from app.utils.poll_closure import monitor_poll_closure

# Time
from datetime import datetime, timezone, timedelta

from app.constants.global_settings import REVOTE_POLL_CLOSE_TIME, RV_DAY_ERR, RV_DAY_QUESTION, RV_DAY_OPTIONS

revote_day_router = Router()

# Create a poll for day revote
@revote_day_router.message(Command('revote_day'))
async def handle_command(msg: types.Message) -> None:
    # Chat info
    chat_id = msg.chat.id

    # Get group data
    group = get_data('groups', chat_id)     

    # It's important to check state
    if group.get('day') == 'pending' or group.get('time') == 'pending':
        await msg.answer(RV_DAY_ERR)
        return

    # Init closetime (48 hours by default)
    close_time = int((datetime.now(timezone.utc).now() + timedelta(hours=REVOTE_POLL_CLOSE_TIME)).timestamp())

    # Create a poll with question and options
    day_poll = await msg.bot.send_poll(chat_id=chat_id,
                                       question=RV_DAY_QUESTION,
                                       options=RV_DAY_OPTIONS,
                                       is_anonymous=True)
    
    # Add poll data to the db
    add_data('polls', day_poll.poll.id,
             {"chat_id": chat_id, 
              "message_id": day_poll.message_id,
              "title": f"revote_day",
              "close_time": close_time})
    
    # And create async monitor task
    asyncio.create_task(monitor_poll_closure(msg.bot, chat_id,
                                             day_poll.message_id, day_poll.poll.id,
                                             close_time))