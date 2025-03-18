# --
# Place all keyboards here
# --
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Generates start keyboard for the DM
# And also generates special URL with all necessary permissions.
def start_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Add to the group", url='https://t.me/your_bot_username?startgroup=true&admin=change_info+restrict_members+delete_messages+pin_messages+invite_users')]])
    return kb