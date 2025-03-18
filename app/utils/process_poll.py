# DB
from app.database.db import delete_data, get_data, update_data

from app.constants.global_settings import (TIE_MESSAGE, ADD_PLACE_CHANGE, ADD_PLACE_DECLINE, 
                                           REMOVE_PLACE_CHANGE, REMOVE_PLACE_DECLINE, REVOTE_DAY_CHANGE, 
                                           REVOTE_TIME_CHANGE)


async def process_poll(bot, chat_id: int, msg_id: int, poll_id: int) -> None:
    try:
        # Try to stop current poll
        poll_results = await bot.stop_poll(chat_id, msg_id)

        # Get all options from the poll
        # and calculate max vote
        options = poll_results.options
        max_votes = max(option.voter_count for option in options)

        # Get all options that have this max vote count
        winning_options = [option.text for option in options if option.voter_count == max_votes]

        # Check for tie
        if len(winning_options) > 1:

            # If it's a tie we should notify user about it
            await bot.send_message(chat_id, 
                                    TIE_MESSAGE,
                                    reply_to_message_id=msg_id)
            
            # Unpin the message
            await bot.unpin_chat_message(chat_id=chat_id, message_id=msg_id)

            # And delete temp poll from the DB reference
            delete_data('polls', poll_id)

            # Return, because we don't want to process further
            return 

        # If no tie, select the winner from the list
        winner_option = winning_options[0]

    # Handle error and print it
    except Exception as e:
        print(f"Failed to stop the poll: {e}")
        return

    # Fetch poll data
    poll_info = get_data("polls", poll_id)
    group = get_data('groups', chat_id)

    # Extract title to work with it later
    title = poll_info['title'] 


    # Check title and extract placename
    if title.startswith('add_'):

        # Handle and check options
        if winner_option != 'Ні':

            # Fetch places 
            places = group.get('places')
            placename = title.split('_')[1]

            # Append new place
            places.append(placename)

            # And update places 
            update_data(chat_id, {'places': places})

            # Notify
            await bot.send_message(chat_id, text=f'<b>{placename}</b> {ADD_PLACE_CHANGE}')
        
        # Otherwise notify about refuse
        else:
            await bot.send_message(chat_id, text=f'<b>{placename}</b> {ADD_PLACE_DECLINE}')

    # Handle remove title and extract placename to remove  
    elif title.startswith('remove_'):

        # Handle options
        if winner_option != 'Ні':

            # Fetch places 
            places = get_data('groups', chat_id).get('places')
            placename = title.split('_')[1]

            # Remove place from the list
            places.remove(placename)

            # Update data with new list
            update_data(chat_id, {'places': places})

            # Notify
            await bot.send_message(chat_id, text=f'<b>{placename}</b> {REMOVE_PLACE_CHANGE}')

        # Otherwise notify about refuse
        else:
            await bot.send_message(chat_id, text=f'<b>{placename}</b> {REMOVE_PLACE_DECLINE}')
    
    # Handle and check revote day poll
    elif title.startswith('revote_day'):

        # Update data 
        update_data(chat_id, {"day": winner_option})

        # Notify about winner
        await bot.send_message(chat_id, f"{REVOTE_DAY_CHANGE} <b>{winner_option}</b>")
    
    # Handle and check revote time poll
    elif title.startswith('revote_time'):

        # Update data
        update_data(chat_id, {"time": winner_option})

        # Notify about winner
        await bot.send_message(chat_id, f"{REVOTE_TIME_CHANGE} <b>{winner_option}</b>")
    
    # It's necessary to clean up a bit
    # Unpin message
    # Delete processed polls from the database
    await bot.unpin_chat_message(chat_id=chat_id, message_id=msg_id)
    delete_data('polls', poll_id)