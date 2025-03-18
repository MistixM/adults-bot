# Aiogram tools
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, Poll
import asyncio

# App utils and DBs
from app.keyboards.inline import start_keyboard
from app.utils.meeting_cycle import process_meeting, start_meeting_cycle
from app.utils.google_drive import upload_to_drive
from app.database.db import add_data, get_data, delete_data, update_data

from datetime import datetime
from zoneinfo import ZoneInfo

# Global settings
from app.constants.global_settings import (GROUP_START_MESSAGE, POLL_DAY_QUESTION, POLL_DAY_OPTIONS, POLL_TIME_QUESTION, 
                                           POLL_TIME_OPTIONS, DM_START_MESSAGE, PHOTO_HASHTAG_TRIGGER, 
                                           MIN_VOTES, REVOTE_DAY_CHANGE, REVOTE_TIME_CHANGE, ADD_PLACE_CHANGE,
                                           ADD_PLACE_DECLINE, REMOVE_PLACE_CHANGE, REMOVE_PLACE_DECLINE, OWNER_ID, START_VIDEO_PATH)

# Other
import os

start_router = Router()


# Handles start command process
# Handles start command process
@start_router.message(CommandStart())
async def handle_start(msg: types.Message) -> None:
    # Get chat data
    # And register group in the database if it doesn't exist
    chat_id = msg.chat.id
    if not get_data('groups', chat_id):
        args = msg.text.split(maxsplit=1)

        if msg.chat.type == "private":
            await msg.answer(text=DM_START_MESSAGE, reply_markup=start_keyboard())
            return
        
        if len(args) < 2:
            await msg.answer("Будь ласка, вкажи місця та часовий пояс у форматі:\n/start place1, place2, place 3 Europe/Lisbon")
            return

        places_and_timezone = args[1].rsplit(maxsplit=1)
        if len(places_and_timezone) < 2:
            await msg.answer("Будь ласка, вкажи часовий пояс після списку місць.")
            return

        places = places_and_timezone[0].split(',')
        timezone = places_and_timezone[1]

        try:
            zoneinfo = ZoneInfo(timezone)
            now = datetime.now(zoneinfo)
            print(f"Timezone set correctly: {zoneinfo}. Now time: {now}")
        except Exception:
            await msg.answer(text="Неправильний timezone формат або такого формату не існує. Використовуй формат: Регіон/Місто")
            return
        
        if not '/' in timezone:
            await msg.answer("Будь ласка, вкажи timezone у правильному форматі (e.g Europe/Lisbon)")
            return
        
        admin = await msg.bot.get_chat_member(chat_id, OWNER_ID)

        if admin or await msg.bot.get_chat_member(chat_id, 1266917712):
            add_data("groups", chat_id, {
                "day": "pending",
                "time": "pending",
                "group_title": msg.chat.title,
                "meeting_number": 0,
                "last_place": "None",
                "places": places,
                "timezone": timezone
            })
        else:
            await msg.answer("Будь ласка, вкажи місця для заповнення БД")
            return

    # We should check if bot, indeed, in the group and send appropriate message.
    # By convention group has "-" symbol in the ID (e.g -> -12345678).
    # Direct message vice versa, doesn't have this symbol (e.g -> 12345678).
    if "-" in str(chat_id):
        group_info = get_data('groups', chat_id)

        # Send the photo
        greeting_photo = await msg.answer_photo(photo=FSInputFile(START_VIDEO_PATH))

        # And then caption
        greeting_message = await msg.answer(text=GROUP_START_MESSAGE)

        # Check both states and if they exists we should send the polls
        if group_info['day'] == 'pending' or group_info['time'] == 'pending':
            
            # Pin greeting message
            await msg.bot.pin_chat_message(chat_id, greeting_message.message_id)

            # Send the day poll
            poll_day = await msg.bot.send_poll(chat_id=chat_id,
                        question=POLL_DAY_QUESTION,
                        options=POLL_DAY_OPTIONS,
                        is_anonymous=True,
                        allows_multiple_answers=True)

            # Add poll info to DB to track it later
            add_data("polls", poll_day.poll.id, {"chat_id": chat_id, 
                                                "message_id": poll_day.message_id,
                                                "title": "day"})

            # Pin day poll 
            await msg.bot.pin_chat_message(chat_id, poll_day.message_id)
            
            # Just to prevent unwanted spamming
            await asyncio.sleep(5)
            
            # Create time poll
            poll_time = await msg.bot.send_poll(chat_id=chat_id,
                                                question=POLL_TIME_QUESTION,
                                                options=POLL_TIME_OPTIONS,
                                                is_anonymous=True,
                                                allows_multiple_answers=True,
                                                )

            # Add poll info to the database to track it later
            add_data("polls", poll_time.poll.id, {"chat_id": chat_id, 
                                                "message_id": poll_time.message_id,
                                                "title": "time"})

            # And pin it as well
            await msg.bot.pin_chat_message(chat_id, poll_time.message_id)


    # If current chat is a DM we should suggest user to add our bot to the group
    else:
        await msg.answer(text=DM_START_MESSAGE,
                         reply_markup=start_keyboard())


# Photo handler
# Checks for new incoming photos
@start_router.message(F.photo)
async def handle_photo(msg: types.Message) -> None:
    # Get chat info and DB
    chat_id = msg.chat.id
    group = get_data('groups', chat_id)

    cycle_status = group.get('cycle_status')
    
    # Check if caption exists
    # Check if caption has required hashtag to hook
    # And lastly check cycle status (so we can make sure that was during meeting day)
    if msg.caption and PHOTO_HASHTAG_TRIGGER in msg.caption and cycle_status in ["meeting_day", "photo_reminder"]:

        meeting_number = group.get('meeting_number')
        
        # Get all necessary info about photo
        # [-1] -> means get the photo in the highests quality
        photo = msg.photo[-1]
        file_id = photo.file_id
        
        # Download the file 
        # And store it temporarily
        file = await msg.bot.get_file(file_id)
        file_path = file.file_path
        downloaded_file = await msg.bot.download_file(file_path)
        local_filename = f"{file_id}.jpg"

        with open(local_filename, 'wb') as ph:
            ph.write(downloaded_file.read())
        
        # Push that file to the Google Drive folder with group title and current meeting number
        await upload_to_drive(local_filename, msg.chat.title, f"{msg.chat.title} #{meeting_number}")

        # Remove temp photo from the system
        os.remove(local_filename)


# Handle and monitor all poll changes.
# This function will be triggered when poll voted or some actions was perfomred. 
@start_router.poll()
async def handle_answer_poll(poll: Poll):
    # Get all necessary poll data
    total_voter_count = poll.total_voter_count
    poll_id = poll.id

    poll_info = get_data("polls", poll_id)
    chat_id = poll_info['chat_id']

    group = get_data('groups', chat_id)

    # Try to get title and chat_id
    try:
        poll_title = poll_info['title']
    except Exception as e:
        print(f"Warn [start.py]: {e}")
        return
    
    # Each triggered poll should be checked here.
    # Poll must have at least 15 votes.
    # Poll shouldn't be closed.
    # Poll shouldn't have "meeting_poll" status (because it will automatically close meeting poll)

    if total_voter_count >= MIN_VOTES and not poll.is_closed and poll_title != "meeting_poll":
        
        # Get options and determine the winner
        options = poll.options
        winner_option = max(options, key=lambda option: option.voter_count).text

        # Stop the poll from the fetched ID from the DB
        await poll.bot.stop_poll(chat_id, poll_info['message_id'])

        # Try to unpin message 
        try:
            await poll.bot.unpin_chat_message(chat_id)
        except Exception as e:
            print(f"An error occured while unpinning message [start.py]: {e}")

        
        # If poll is a day
        if poll_title == 'day':

            print(f'{chat_id} -> {winner_option}')

            # Update day data in the DB
            update_data(chat_id, {"day": winner_option})

            group = get_data('groups', chat_id)

            # We should also check both statuses
            # And if they are not "pending" start meeting cycle
            if not 'pending' in [group.get('day'), group.get('time')]:
                print("Process meeting")

                await process_meeting(chat_id, group.get('day'), group.get('time'))

                await start_meeting_cycle(poll.bot, chat_id)
            else:
                print(group.get('day'))
                print(group.get('time'))

        # If poll is a time 
        elif poll_title == 'time':

            print(f'{chat_id} -> {winner_option}')

            # Update time in the DB
            update_data(chat_id, {"time": winner_option})
            
            group = get_data('groups', chat_id)

            # We should also check both statuses
            # And if they are not "pending" start meeting cycle
            if not 'pending' in [group.get('day'), group.get('time')]:
                print("Process meeting")

                await process_meeting(chat_id, group.get('day'), group.get('time'))

                await start_meeting_cycle(poll.bot, chat_id)
            else:
                print(group.get('day'))
                print(group.get('time'))

            
        # If poll is a revote day
        elif poll_title == "revote_day":
            # Update the day
            update_data(chat_id, {"day": winner_option})
            
            # Notify all users
            await poll.bot.send_message(chat_id, f"{REVOTE_DAY_CHANGE} <b>{winner_option}</b>")
        
        # If poll is a revote time
        elif poll_title == 'revote_time':
            # Update time
            update_data(chat_id, {"time": winner_option})

            # Notify all users
            await poll.bot.send_message(chat_id, f"{REVOTE_TIME_CHANGE} <b>{winner_option}</b>")

        # If poll title starts with 'add' 
        # We should handle it and parse new place to add
        elif poll_title.startswith('add_'):

            # Extract data from the title
            title = poll_info['title']
            placename = title.split('_')[1]

            # Check and handle winner options
            if winner_option != 'Ні':
                
                # Get current places and append new item to the list
                places = group.get('places')
                places.append(placename)

                # Push changes to the DB
                update_data(chat_id, {'places': places})

                # Notify users about change
                await poll.bot.send_message(chat_id, text=f'<b>{placename}</b> {ADD_PLACE_CHANGE}')
            
            # Otherwise we just notify users about refusing
            else:
                await poll.bot.send_message(chat_id, text=f"<b>{placename}</b> {ADD_PLACE_DECLINE}")
        
        # If poll starts with remove
        # We should handle and parse place to remove
        elif poll_title.startswith("remove_"):

            # Extract data from the title
            title = poll_info['title']
            placename = title.split('_')[1]
            
            # Again check winner option
            if winner_option != 'Ні':
                
                # Get and remove place from the current list
                places = group.get('places')
                places.remove(placename)
                
                # Push changes to the DB
                update_data(chat_id, {'places': places})

                # Notify users about changes
                await poll.bot.send_message(chat_id, text=f'<b>{placename}</b> {REMOVE_PLACE_CHANGE}')
            
            # Otherwise just notify about refusing
            else:
                await poll.bot.send_message(chat_id, text=f'<b>{placename}</b> {REMOVE_PLACE_DECLINE}')
        
        # It's important to delete poll data after every win
        delete_data("polls", poll_id)

