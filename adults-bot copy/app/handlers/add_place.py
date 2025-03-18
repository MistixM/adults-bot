# Aiogram tools
from aiogram import Router, types
from aiogram.filters import Command
import asyncio

# Db and utils
from app.database.db import add_data, get_data
from app.utils.poll_closure import monitor_poll_closure

# Time 
from datetime import datetime, timezone, timedelta

from app.constants.global_settings import (ADD_PLACE_ERR, ADD_PLACE_DIGIT_ERR, ADD_PLACE_ARG_ERR, 
                                           ADD_PLACE_EXIST_ERR, ADD_PLACE_QUESTION, POLL_CLOSE_TIME)

add_router = Router()


# Creates poll for the new place suggestion
# Accept argument as a placename
@add_router.message(Command('add_place'))
async def handle_command(msg: types.Message) -> None:
    # Get chat info
    chat_id = msg.chat.id
    args = msg.text.split(maxsplit=1)

    # Extract data from the command 
    # And get group data from the DB
    group = get_data('groups', chat_id)
    place_name = args[1]

    # Users should pass initial start loop (vote default time and day)
    # So we must check it here
    if group.get('day') == 'pending' or group.get('time') == 'pending':
        await msg.answer(ADD_PLACE_ERR)
        return
    
    # Place mustn't be digit
    if place_name.isdigit():
        await msg.answer(ADD_PLACE_DIGIT_ERR)
        return

    # Check if arguments exists
    if len(args) < 2:
        await msg.answer(ADD_PLACE_ARG_ERR)
        return
    
    # Important to check place in the database to prevent duplicates
    if place_name in group.get('places'):
        await msg.answer(ADD_PLACE_EXIST_ERR)
        return
    
    # Init closetime (24 hours by default)
    close_time = int((datetime.now(timezone.utc).now() + timedelta(hours=POLL_CLOSE_TIME)).timestamp())

    # Create poll with question and its options
    place_poll = await msg.bot.send_poll(chat_id=chat_id,
                            question=f"<b>{place_name}</b> {ADD_PLACE_QUESTION}",
                            options=['Так', 'Ні'],
                            is_anonymous=True,
                            )
    
    # Add poll info to the database
    add_data('polls', place_poll.poll.id, {"chat_id": chat_id,
                                           "message_id": place_poll.message_id,
                                           "title": f"add_{place_name}",
                                           "close_time": close_time})
    
    
    # Start asynchronous monitoring task
    asyncio.create_task(monitor_poll_closure(msg.bot, chat_id, 
                                             place_poll.message_id, place_poll.poll.id, 
                                             close_time))