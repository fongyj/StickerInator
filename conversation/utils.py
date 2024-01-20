import logging
from dotenv import load_dotenv
import os
from telegram import Update
from telegram.constants import ParseMode

load_dotenv()

async def send_message(update: Update, message):
    # sends message with markdown parse mode.
    bot = update.get_bot()
    await bot.send_message(
        update.effective_chat.id, message, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True
    )

async def log_info(info, bot):
    logging.info(info)
    await bot.send_message(os.environ.get("LOG_ID"), info)
