from dotenv import load_dotenv
import logging
import os

load_dotenv()

from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)
from telegram.error import BadRequest
from telegram.constants import ParseMode

from conversation.messages import (
    STICKER_FROM_SET_MESSAGE,
    DELETE_PACK_CONFIRMATION_MESSAGE,
    DELETE_PACK_SUCCESS_MESSAGE,
    SET_NOT_FOUND_MESSAGE,
    INVALID_SET_MESSAGE,
)
from conversation.cancel_command import cancel

SELECTING_PACK, CONFIRM_DELETE = map(chr, range(2))


async def delete_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("{}: delete pack".format(update.effective_user.name))
    context.user_data["operation"] = "delete pack"
    await update.message.reply_text(STICKER_FROM_SET_MESSAGE)
    return SELECTING_PACK


async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sticker"] = update.message.sticker
    sticker_set = context.user_data["sticker"].set_name
    logging.info(
        "{}: selected sticker pack {}".format(update.effective_user.name, sticker_set)
    )
    if not sticker_set.endswith("_by_" + os.environ.get("BOT_NAME")):
        await update.message.reply_text(INVALID_SET_MESSAGE)
        await update.message.reply_text(STICKER_FROM_SET_MESSAGE)
        return SELECTING_PACK
    await update.message.reply_text(DELETE_PACK_CONFIRMATION_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2)
    return CONFIRM_DELETE


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.text.lower() == "yes":
            bot = update.get_bot()
            sticker_set = context.user_data["sticker"].set_name
            await bot.delete_sticker_set(sticker_set)
            await update.message.reply_text(
                DELETE_PACK_SUCCESS_MESSAGE.format(sticker_set)
            )
            logging.info(
                "{}: deleted pack {}".format(update.effective_user.name, sticker_set)
            )
        else:
            await update.message.reply_text(DELETE_PACK_CONFIRMATION_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2)
            return CONFIRM_DELETE
    except BadRequest as e:
        await update.message.reply_text(SET_NOT_FOUND_MESSAGE)
    return ConversationHandler.END


def delete_pack_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("delpack", delete_pack)],
        states={
            SELECTING_PACK: [
                MessageHandler(filters.Sticker.ALL & ~filters.COMMAND, select_pack)
            ],
            CONFIRM_DELETE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
