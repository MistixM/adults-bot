# Aiogram tools
from aiogram import Router, types
from aiogram.filters import Command
import asyncio

# Utils and DB
from app.database.db import add_data, get_data
from app.utils.poll_closure import monitor_poll_closure

# Time
from datetime import datetime, timezone, timedelta

from app.constants.global_settings import (POLL_CLOSE_TIME, RM_PLACE_ERR, RM_PLACE_DIGIT_ERR, 
                                           RM_PLACE_ARG_ERR, RM_PLACE_EXIST_ERR, RM_PLACE_QUESTION)
remove_router = Router()

# Creates a poll with removal suggestion
@remove_router.message(Command('remove_place'))
async def handle_command(msg: types.Message) -> None:
    # Get chat info
    chat_id = msg.chat.id

    # Get argument and convert it to the placename
    args = msg.text.split(maxsplit=1)
    group = get_data('groups', chat_id)
    place_name = args[1]

    # Users should pass initial start loop (vote default time and day)
    # So we must check it here
    if group.get('day') == 'pending' or group.get('time') == 'pending':
        await msg.answer(RM_PLACE_ERR)
        return

    # Place mustn't be digit
    if place_name.isdigit():
        await msg.answer(RM_PLACE_DIGIT_ERR)
        return

    # Check if arguments exists
    if len(args) < 2:
        await msg.answer(RM_PLACE_ARG_ERR)
        return

    # Important place availability in the database
    if not place_name in group.get('places'):
        await msg.answer(RM_PLACE_EXIST_ERR)
        return

    # Init closetime (24 hours by default)
    close_time = int((datetime.now(timezone.utc).now() + timedelta(hours=POLL_CLOSE_TIME)).timestamp())
    
    # Create a poll with question and its options
    place_poll = await msg.bot.send_poll(chat_id=chat_id,
                                         question=f'<b>{place_name}</b> {RM_PLACE_QUESTION}',
                                         options=['Так', 'Ні'],
                                         is_anonymous=True,
                                         )
    
    # Add poll to the database
    add_data('polls', place_poll.poll.id, {"chat_id": chat_id,
                                           "message_id": place_poll.message_id,
                                           "title": f"remove_{place_name}",
                                           "close_time": close_time})
    
    # Start asynhronous task
    asyncio.create_task(monitor_poll_closure(msg.bot, chat_id,
                                             place_poll.message_id, place_poll.poll.id,
                                             close_time))