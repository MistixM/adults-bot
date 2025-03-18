import asyncio

from datetime import datetime
from zoneinfo import ZoneInfo

from app.utils.process_poll import process_poll

from app.database.db import get_data

# Start monitoring poll process
# Wait before time is over and start process
async def monitor_poll_closure(bot, chat_id: int, msg_id: int, poll_id: int, close_time) -> None:
    
    # Get the group data from the database
    # Get the timezone to adjust the correct timezone for the poll closure.
    group = get_data('groups', chat_id)
    timezone = group.get('timezone')
    
    # Get current time with a timezone specified.
    current_time = datetime.now(ZoneInfo(timezone))

    # Calculate close time date with timezone.
    close_time_date = datetime.fromtimestamp(close_time, ZoneInfo(timezone))

    # Calculate difference between them
    time_difference = close_time_date - current_time

    # Adjust sleep duration to wait
    sleep_duration = max(0, time_difference.total_seconds())
    
    # Sleep and process once ready.
    await asyncio.sleep(sleep_duration)
    await process_poll(bot, chat_id, msg_id, poll_id)