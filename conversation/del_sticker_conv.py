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

from conversation.messages import (
    DELETE_STICKER_MESSAGE,
    LAST_STICKER_MESSAGE,
    DELETE_STICKER_CONFIRMATION_MESSAGE,
    STICKER_NOT_FOUND_MESSAGE,
    SET_NOT_FOUND_MESSAGE,
    DELETE_PACK_SUCCESS_MESSAGE,
    DELETE_STICKER_SUCCESS_MESSAGE,
    INVALID_SET_MESSAGE,
    STICKER_FROM_SET_MESSAGE,
)
from conversation.cancel_command import cancel

SELECTING_PACK, CONFIRM_DELETE = map(chr, range(2))


async def delete_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("{}: delete sticker".format(update.effective_user.name))
    context.user_data["operation"] = "delete sticker"
    await update.message.reply_text(DELETE_STICKER_MESSAGE)
    return SELECTING_PACK


async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        bot = update.get_bot()
        context.user_data["sticker"] = update.message.sticker
        sticker_set = context.user_data["sticker"].set_name
        logging.info(
            "{}: selected sticker pack {}".format(
                update.effective_user.name, sticker_set
            )
        )
        if not sticker_set.endswith("_by_" + os.environ.get("BOT_NAME")):
            await update.message.reply_text(INVALID_SET_MESSAGE)
            await update.message.reply_text(DELETE_STICKER_MESSAGE)
            return SELECTING_PACK
        sticker_set_info = await bot.get_sticker_set(sticker_set)

        # Iterate through the stickers in the sticker set
        for sticker_info in sticker_set_info.stickers:
            if context.user_data["sticker"].file_id == sticker_info.file_id:
                if len(sticker_set_info.stickers) == 1:
                    context.user_data["last"] = True
                    await update.message.reply_text(LAST_STICKER_MESSAGE)
                else:
                    context.user_data["last"] = False
                    await update.message.reply_text(DELETE_STICKER_CONFIRMATION_MESSAGE)
                return CONFIRM_DELETE

        # If the sticker wasn't found in the set
        await update.message.reply_text(STICKER_NOT_FOUND_MESSAGE)
    except BadRequest as e:
        await update.message.reply_text(SET_NOT_FOUND_MESSAGE)
    return ConversationHandler.END


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.text.lower() == "yes":
            bot = update.get_bot()
            sticker_set = context.user_data["sticker"].set_name
            sticker = context.user_data["sticker"].file_id
            if context.user_data["last"]:
                await bot.delete_sticker_set(sticker_set)
                await update.message.reply_text(
                    DELETE_PACK_SUCCESS_MESSAGE.format(sticker_set)
                )
            else:
                await bot.delete_sticker_from_set(sticker)
                await update.message.reply_text(
                    DELETE_STICKER_SUCCESS_MESSAGE.format(sticker_set)
                )
                logging.info(
                    "{}: deleted sticker from {}".format(
                        update.effective_user.name, sticker_set
                    )
                )
        else:
            await update.message.reply_text(DELETE_STICKER_CONFIRMATION_MESSAGE)
            return CONFIRM_DELETE
    except BadRequest as e:
        await update.message.reply_text(SET_NOT_FOUND_MESSAGE)
    return ConversationHandler.END


def delete_sticker_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("delsticker", delete_sticker)],
        states={
            SELECTING_PACK: [MessageHandler(filters.Sticker.ALL, select_pack)],
            CONFIRM_DELETE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
