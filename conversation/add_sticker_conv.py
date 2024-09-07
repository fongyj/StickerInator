import asyncio
import os

from telegram import Update, InputSticker
from telegram.constants import StickerFormat
from telegram.error import TelegramError
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from conversation.cancel_command import cancel
from conversation.messages import (
    IMAGE_STICKER_MESSAGE,
    VIDEO_STICKER_MESSAGE,
    STICKER_FROM_PACK_MESSAGE,
    ADD_SUCCESS_MESSAGE,
    INVALID_PACK_MESSAGE,
    UNHANDLED_TELEGRAM_ERROR_MESSAGE,
    ACTIVE_COMMAND_MESSAGE,
)
from conversation.new_pack_conv import (
    SELECTING_STICKER,
    SELECTING_DURATION,
    SELECTING_EMOJI,
    select_sticker,
    select_duration,
    select_emoji,
)
from conversation.utils import log_info

SELECTING_PACK = map(chr, range(7, 8))


async def new_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'operation' in context.user_data:
        await update.message.reply_text(ACTIVE_COMMAND_MESSAGE.format(context.user_data['operation']))
        return ConversationHandler.END

    await log_info("{}: add sticker".format(update.effective_user.name), update.get_bot())
    context.user_data["final_state"] = lambda u, c: add_sticker(u, c)
    context.user_data["stickers"] = list()
    context.user_data["operation"] = "add sticker"
    context.user_data["conversation_key"] = (update._effective_chat.id, update._effective_user.id)
    await update.message.reply_text(STICKER_FROM_PACK_MESSAGE)
    return SELECTING_PACK


async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await log_info("{}: selected sticker pack".format(update.effective_user.name), update.get_bot())
    set_name = update.message.sticker.set_name
    if not set_name.endswith("_by_" + os.environ.get("BOT_NAME")):
        await update.message.reply_text(INVALID_PACK_MESSAGE)
        await update.message.reply_text(STICKER_FROM_PACK_MESSAGE)
        return SELECTING_PACK
    bot = update.get_bot()
    try:
        sticker_set = await bot.do_api_request("get_sticker_set", {"name": set_name})
    except TelegramError as e:
        await update.message.reply_text(e.message)
        await update.message.reply_text(STICKER_FROM_PACK_MESSAGE)
        return SELECTING_PACK
    context.user_data["set_name"] = set_name
    context.user_data["sticker_count"] = len(sticker_set["stickers"])
    if sticker_set["stickers"][0]["is_video"]:
        context.user_data["type"] = StickerFormat.VIDEO
        await update.message.reply_text(VIDEO_STICKER_MESSAGE)
    else:
        context.user_data["type"] = StickerFormat.STATIC
        await update.message.reply_text(IMAGE_STICKER_MESSAGE)
    return SELECTING_STICKER


async def add_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = update.get_bot()
    try:
        for sticker, emoji in context.user_data["stickers"]:
            if isinstance(sticker, asyncio.Task):
                sticker = await sticker
            await bot.add_sticker_to_set(update.effective_user.id, context.user_data["set_name"], sticker=InputSticker(sticker, emoji))
        sticker_count = len(context.user_data["stickers"])
        await update.callback_query.message.reply_text(ADD_SUCCESS_MESSAGE.format(sticker_count))
        await log_info(
            "{}: added {} sticker(s)".format(update.effective_user.name, sticker_count),
            update.get_bot()
        )
    except TelegramError as te:
        await update.callback_query.message.reply_text(te.message)
        await update.callback_query.message.reply_text(UNHANDLED_TELEGRAM_ERROR_MESSAGE)
        await log_info("{}: error adding sticker(s) {}".format(update.effective_user.name, te.message), update.get_bot())
    context.user_data.pop("operation")
    return ConversationHandler.END


def get_add_sticker_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("addsticker", new_sticker)],
        states={
            SELECTING_PACK: [
                MessageHandler(filters.Sticker.ALL & ~filters.COMMAND, select_pack)
            ],
            SELECTING_STICKER: [
                CallbackQueryHandler(select_sticker),
                MessageHandler(filters.ALL & ~filters.COMMAND, select_sticker)
            ],
            SELECTING_DURATION: [
                CallbackQueryHandler(select_duration),
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_duration)
            ],
            SELECTING_EMOJI: [
                CallbackQueryHandler(select_emoji),
                MessageHandler(filters.ALL & ~filters.COMMAND, select_emoji)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
