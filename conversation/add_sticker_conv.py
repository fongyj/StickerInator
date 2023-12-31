import logging

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
from telegram.constants import StickerFormat
import os

from conversation.new_pack_conv import (
    SELECTING_STICKER,
    SELECTING_DURATION,
    SELECTING_EMOJI,
    select_sticker,
    select_duration,
    select_emoji,
)
from conversation.messages import (
    IMAGE_STICKER_MESSAGE,
    VIDEO_STICKER_MESSAGE,
    STICKER_FROM_SET_MESSAGE,
    ADD_SUCCESS_MESSAGE,
    INVALID_SET_MESSAGE,
)
from conversation.cancel_command import cancel

SELECTING_PACK = map(chr, range(7, 8))


async def new_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("{}: add sticker".format(update.effective_user.name))
    context.user_data["final_state"] = lambda u, c: add_sticker(u, c)
    context.user_data["stickers"] = list()
    context.user_data["operation"] = "add sticker"
    await update.message.reply_text(STICKER_FROM_SET_MESSAGE)
    return SELECTING_PACK


async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_name = update.message.sticker.set_name
    logging.info(
        "{}: selected sticker pack {}".format(update.effective_user.name, set_name)
    )
    if not set_name.endswith("_by_" + os.environ.get("BOT_NAME")):
        await update.message.reply_text(INVALID_SET_MESSAGE)
        await update.message.reply_text(STICKER_FROM_SET_MESSAGE)
        return SELECTING_PACK
    bot = update.get_bot()
    sticker_set = await bot.get_sticker_set(set_name)
    context.user_data["set_name"] = set_name
    context.user_data["sticker_count"] = len(sticker_set.stickers)
    if sticker_set.is_video:
        context.user_data["type"] = StickerFormat.VIDEO
        await update.message.reply_text(VIDEO_STICKER_MESSAGE)
    else:
        context.user_data["type"] = StickerFormat.STATIC
        await update.message.reply_text(IMAGE_STICKER_MESSAGE)
    return SELECTING_STICKER


async def add_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = update.get_bot()
    for sticker in context.user_data["stickers"]:
        await bot.add_sticker_to_set(
            update.effective_user.id, context.user_data["set_name"], sticker=sticker
        )
    sticker_count = len(context.user_data["stickers"])
    await update.message.reply_text(ADD_SUCCESS_MESSAGE.format(sticker_count))
    logging.info(
        "{}: added {} sticker(s)".format(update.effective_user.name, sticker_count)
    )
    return ConversationHandler.END


def get_add_sticker_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("addsticker", new_sticker)],
        states={
            SELECTING_PACK: [
                MessageHandler(filters.Sticker.ALL & ~filters.COMMAND, select_pack)
            ],
            SELECTING_STICKER: [
                MessageHandler(filters.ALL & ~filters.COMMAND, select_sticker)
            ],
            SELECTING_DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_duration)
            ],
            SELECTING_EMOJI: [
                MessageHandler(filters.ALL & ~filters.COMMAND, select_emoji)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
