# Aiogram tools
from aiogram import Bot
import asyncio

# DB
from app.database.db import get_data, update_data, add_data, delete_data

# Other
import random
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.constants.global_settings import (WAITING_POLL_STATUS_DELAY, POLL_ACTIVE_STATUS_DELAY, NOTIFYING_USERS_STATUS_DELAY, 
                                           MEETING_DAY_STATUS_DELAY, PLACES_LIMIT, PLACE_REMIND_MESSAGE, PHOTO_REMIND_MESSAGE)



# A meeting cycle that checks current status and perform some meeting actions:
# 1. creating poll
# 2. detecting poll status and managing status

async def start_meeting_cycle(bot: Bot, chat_id: int) -> None:
    while True:
        
        print("meeting cycle process")

        # Get all the important data from the DB
        group_data = get_data('groups', chat_id)

        # Status
        cycle_status = group_data.get('cycle_status', 'waiting_poll')
        
        # Time
        poll_time = group_data.get('time')
        poll_day = group_data.get('day')
        next_meeting_date_str = group_data.get('next_meeting_date')

        # Crucial items
        places = group_data.get('places')
        meeting_number = group_data.get('meeting_number')
        last_place = group_data.get('last_place')
        group_title = group_data.get('group_title')

        # If for some unknown reason group does not have meetin date -> just wait for a while
        if not next_meeting_date_str:
            await asyncio.sleep(10)
            continue
        
        # Create a next meeting date with datetime format
        next_meeting_date = datetime.strptime(next_meeting_date_str, "%Y-%m-%d")
        next_meeting_date = next_meeting_date.replace(tzinfo=ZoneInfo(group_data.get('timezone')))
        
        # today = datetime.today()
        today = datetime.now(ZoneInfo(group_data.get('timezone')))

        # Handle all statuses 
        # If current status is "waiting_poll" bot will calculate poll start
        # And will post it on the right date
        if cycle_status == "waiting_poll":

            # Five days before meeting
            poll_start_date = next_meeting_date - timedelta(days=WAITING_POLL_STATUS_DELAY)

            # If it's time to post the poll
            if today >= poll_start_date:

                # Shuffle places and limit them to 6
                shuffled_places = random.sample(places, len(places))[:PLACES_LIMIT]

                # If we got previous winner we should remove it            
                if last_place in shuffled_places:
                    shuffled_places.remove(last_place)
                
                # Start the meeting poll
                meeting_poll = await bot.send_poll(chat_id=chat_id,
                                                   question=f"{group_title} #{meeting_number}\n🗓️ {next_meeting_date.strftime('%d.%m.%Y')} після {poll_time}",
                                                   options=shuffled_places,
                                                   is_anonymous=True)

                # Pin it
                await bot.pin_chat_message(chat_id, meeting_poll.message_id)

                # It's important to update status 
                # and provide some additional poll informations to track
                update_data(chat_id, {
                    "cycle_status": "poll_active",
                    "meeting_poll_id": meeting_poll.poll.id,
                    "meeting_poll_msg_id": meeting_poll.message_id
                })

                # We should also add some data to the temp 'polls' reference
                # Just to make sure that we can track it later (if required)
                add_data('polls', meeting_poll.poll.id, {
                    "chat_id": chat_id,
                    "message_id": meeting_poll.message_id,
                    "title": "meeting_poll",
                })
                
            # If today is not a right date wait 3600 seconds (1 hour)
            else:
                await asyncio.sleep(3600)
        
        # If current status is 'poll_active' we should remind to users about poll
        elif cycle_status == "poll_active":
            
            # Three days before meeting
            notify_date = next_meeting_date - timedelta(days=POLL_ACTIVE_STATUS_DELAY)

            print(f"Notify poll date: {notify_date}")

            # If current day has match with notify_date
            if today >= notify_date: 

                # Remind with message about the poll
                await bot.send_message(chat_id, 
                                       text=PLACE_REMIND_MESSAGE,
                                       reply_to_message_id=group_data.get('meeting_poll_msg_id'))
                
                # Update status
                update_data(chat_id, {"cycle_status": "notifying_users"})
            
            # Otherwise wait 3600 seconds (1 hour)
            else:
                await asyncio.sleep(3600)
        
        # If current status is 'notifying_users' we should collect results from the poll
        elif cycle_status == "notifying_users":
            
            # One day before meeting
            close_poll_date = next_meeting_date - timedelta(days=NOTIFYING_USERS_STATUS_DELAY)
            poll_message_id = group_data.get('meeting_poll_msg_id')

            # If today is a right date
            if today >= close_poll_date:
                try:
                    # Try to stop the poll
                    poll_results = await bot.stop_poll(chat_id, poll_message_id)

                    # Get options from the poll
                    options = poll_results.options

                    # Calculate winner
                    max_votes = max(option.voter_count for option in options)
                    winning_options = [option.text for option in options if option.voter_count == max_votes]

                    # Check if we have a tie
                    if len(winning_options) > 1:

                        # If so, pick some random place from the options
                        random_winner = random.choice(options).text

                        # Update data and clear outdated data
                        update_data(chat_id, {"last_place": random_winner,
                                              "meeting_poll_id": None})

                        # Notify users about winner
                        winner_msg = await bot.send_message(chat_id, 
                                            f"{random_winner} 🇺🇦", 
                                            reply_to_message_id=poll_message_id)

                    # If we don't have a tie
                    else:
                        
                        # Choose the winner from the list
                        winning_option = winning_options[0]

                        # Notify users about winner
                        winner_msg = await bot.send_message(chat_id, 
                                            f"{winning_option} 🇺🇦", 
                                            reply_to_message_id=poll_message_id)

                        # Update data and clear outdated data
                        update_data(chat_id, {"last_place": winning_option,
                                            "meeting_poll_id": None})
                    
                    # Pin winner
                    await bot.pin_chat_message(chat_id, winner_msg.message_id)

                    # Clear the poll from the reference
                    delete_data('polls', poll_message_id)

                # Handle error and print it
                except Exception as e:
                    print(f"Poll was closed before or unexpected error occured: {e}")

                # Unpin the message
                await bot.unpin_chat_message(chat_id)

                # And update the status
                update_data(chat_id, {"cycle_status": "meeting_day"})

            # If today does not match with planned date, wait 1 hour
            else:
                await asyncio.sleep(500)
        
        # If current status is a 'meeting_day' 
        # we should remind to users to send the photo from the meeting
        elif cycle_status == "meeting_day":

            # Prepare event time and time to remind (2 hours after meeting time)
            event_time = datetime.strptime(f'{poll_time}:00', "%H:%M")
            reminder_time = next_meeting_date.replace(hour=event_time.hour, minute=event_time.minute) + timedelta(hours=MEETING_DAY_STATUS_DELAY)

            # If today is a right date
            if today >= reminder_time:
                # Send the reminder to the users
                await bot.send_message(chat_id, 
                                       text=PHOTO_REMIND_MESSAGE,
                                       reply_to_message_id=group_data.get('meeting_poll_msg_id'))

                # Update the status
                update_data(chat_id, {"cycle_status": "photo_reminder"})
            
            # Wait if today does not match with reminder time. 
            else:
                await asyncio.sleep(600)

        # If cycle status is 'photo_reminder' we should ensure 
        # that meeting day is over and we good to go to next iteration
        elif cycle_status == "photo_reminder":

            # Calculate tomorrow's date
            tomorrow = next_meeting_date + timedelta(days=1)

            # If today is a right date
            if today >= tomorrow:
                # Unpin the message
                await bot.unpin_chat_message(chat_id)
                
                # Update the status update
                update_data(chat_id, {"cycle_status": "completed"})
            
            # If it's not -> wait 24 hour
            else:
                await asyncio.sleep(86400)
        
        # Finish cycle iteration with completed status
        elif cycle_status == "completed":
            # Update the meeting number
            update_data(chat_id, {"meeting_number": int(meeting_number) + 1})

            # And update the next date according to the DB's data
            await process_meeting(chat_id, poll_day, poll_time)

            # And wait 24 hour
            await asyncio.sleep(86400)


async def process_meeting(chat_id: int, day: str, time) -> None:
    
    # Create weekday map to calculate next meeting more easily
    today = datetime.today()
    weekday_map = {
        "Понеділок": 0, "Вівторок": 1, "Середа": 2, "Четвер": 3,
        "Пʼятниця": 4, "Субота": 5, "Неділя": 6    
    }

    # Get meeting date from the map
    # And calculate days till meeting.
    target_weekday = weekday_map[day]
    days_til_meet = (target_weekday - today.weekday() + 7) % 7

    # Ensure that next meeting is not tomorrow
    if days_til_meet == 1:
        days_til_meet = 8

    # Ensure that next meeting is not today
    if days_til_meet == 0:
        days_til_meet = 7

    # Calculate next meeting date with given info
    next_meeting_date = today + timedelta(days=days_til_meet)

    # Update status and add next meeting date to the database
    update_data(chat_id, {
        "next_meeting_date": next_meeting_date.strftime("%Y-%m-%d"),
        "cycle_status": "waiting_poll"
    })
