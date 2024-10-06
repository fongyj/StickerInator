import asyncio
import logging
import os
from io import BytesIO

import aiohttp
from dotenv import load_dotenv
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
        await bot.send_message(os.environ.get("LOG_ID"), "*\[StickerInator\]* " + info, parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logging.error(e)


def async_request(url):
    return asyncio.create_task(request(url))


async def request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch {url}")
                raise Exception("Failed to fetch sticker")
            content = await response.read()
            return BytesIO(content)


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
    return InlineKeyboardMarkup([get_button_row("NO CROP", "no crop")])


def crop_button():
    return InlineKeyboardMarkup([get_button_row("CROP FIRST 3 SECONDS", "first"),
                                 get_button_row("CROP MIDDLE 3 SECONDS", "middle"),
                                 get_button_row("CROP LAST 3 SECONDS", "last"),
                                 get_button_row("SPEED UP 😃", "speed")])


def emoji_button():
    return InlineKeyboardMarkup([get_button_row(["💬", "😊", "☠️", "💩"], ["💬", "😊", "☠️", "💩"])])


def three_by_one_button(one, two, three):
    return InlineKeyboardMarkup([get_button_row(one, one),
                                 get_button_row(two, two),
                                 get_button_row(three, three)])
