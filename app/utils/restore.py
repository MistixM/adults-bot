# DB
from app.database.db import get_all

# App utils
from app.utils.poll_closure import monitor_poll_closure
from app.utils.process_poll import process_poll
from app.utils.meeting_cycle import start_meeting_cycle

# Other
from datetime import datetime, timezone
import asyncio


# This function will restore lost progress
# If bot accidentaly shutted down it's required to pull up previous processes
# And continue bot work
async def restore_progress(bot) -> None:
    
    # Get all groups from the database
    all_groups = get_all('groups')

    # Iterate over each chat
    for chat_id, group_info in all_groups.items():

        # Fetch cycle status
        cycle_status = group_info.get('cycle_status')

        # If cycle status at least exist we should run meeting cycle again
        # Since each chat has the status the function could easily retreive
        # data and continue cycle work
        if cycle_status:
            asyncio.create_task(start_meeting_cycle(bot, int(chat_id)))
            print(f"Restoring cycle for {chat_id} (status: {cycle_status})")

    # Next we need to restore polls from the database (so that's why we are storing them)
    active_polls = get_all('polls')

    # Iterate over each poll
    for poll_id, poll_info in active_polls.items():

        # Get important data from it
        chat_id = poll_info['chat_id']
        msg_id = poll_info['message_id']

        # Try to get close time (since not all polls have close time 
        # we need to prevent possible issue from the backend side)
        try:
            close_time = poll_info['close_time']

        # Just step to the next iteration if we got poll without close time
        except KeyError:
            print("Unavailable key for close time. Skipping.")
            continue
        
        # Get current time
        current_time = int(datetime.now(timezone.utc).timestamp())

        # If poll is still active we need to start monitoring again
        if close_time > current_time:
            remaining_time = close_time - current_time
            print(f"Recovering: {poll_id}, remaining -> {remaining_time} seconds")

            asyncio.create_task(monitor_poll_closure(bot, chat_id, msg_id, poll_id, close_time))
        
        # Otherwise poll finished and we need to process poll and fetch results
        else:
            print(f"Poll finished: {poll_id}")
            await process_poll(bot, chat_id, msg_id, poll_id)
            