import logging
from dotenv import load_dotenv
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode

load_dotenv()

async def send_message(update: Update, message):
    # sends message with markdown parse mode
    bot = update.get_bot()
    await bot.send_message(
        update.effective_chat.id, message, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True
    )

async def log_info(info, bot):
    logging.info(info)
    try:
        await bot.send_message(os.environ.get("LOG_ID"), info)
    except Exception as e:
        logging.error(e)

def get_button_row(labels, data):
    if type(labels) is not list:
        labels = [labels]
    if type(data) is not list:
        data = [data]
    return [InlineKeyboardButton(l, callback_data=d) for l, d in zip(labels, data)]

def type_button():
    return InlineKeyboardMarkup([get_button_row(["IMAGE", "VIDEO"], ["image", "video"])])

def done_button():
    return InlineKeyboardMarkup([get_button_row("DONE", "done")])

def no_crop_button():
    return InlineKeyboardMarkup([get_button_row("No Crop", "no crop")])

def crop_button():
    return InlineKeyboardMarkup([get_button_row("First 3 Seconds", "first"), 
                                 get_button_row("Middle 3 Seconds", "middle"), 
                                 get_button_row("Last 3 Seconds", "last")])
