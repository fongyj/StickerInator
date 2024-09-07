import os

from dotenv import load_dotenv

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
    STICKER_FROM_PACK_MESSAGE,
    DELETE_PACK_CONFIRMATION_MESSAGE,
    DELETE_PACK_SUCCESS_MESSAGE,
    PACK_NOT_FOUND_MESSAGE,
    INVALID_PACK_MESSAGE,
    ACTIVE_COMMAND_MESSAGE,
)
from conversation.utils import log_info
from conversation.cancel_command import cancel

SELECTING_PACK, CONFIRM_DELETE = map(chr, range(2))


async def delete_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'operation' in context.user_data:
        await update.message.reply_text(ACTIVE_COMMAND_MESSAGE.format(context.user_data['operation']))
        return ConversationHandler.END

    await log_info("{}: delete pack".format(update.effective_user.name), update.get_bot())
    context.user_data["operation"] = "delete pack"
    context.user_data["conversation_key"] = (update._effective_chat.id, update._effective_user.id)
    await update.message.reply_text(STICKER_FROM_PACK_MESSAGE)
    return SELECTING_PACK


async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sticker"] = update.message.sticker
    sticker_set = context.user_data["sticker"].set_name
    await log_info("{}: selected sticker pack {}".format(update.effective_user.name, sticker_set), update.get_bot())
    if not sticker_set.endswith("_by_" + os.environ.get("BOT_NAME")):
        await update.message.reply_text(INVALID_PACK_MESSAGE)
        await update.message.reply_text(STICKER_FROM_PACK_MESSAGE)
        return SELECTING_PACK
    await update.message.reply_text(DELETE_PACK_CONFIRMATION_MESSAGE, parse_mode=ParseMode.HTML)
    return CONFIRM_DELETE


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.text.lower() == "delete pack":
            bot = update.get_bot()
            sticker_set = context.user_data["sticker"].set_name
            await bot.delete_sticker_set(sticker_set)
            await update.message.reply_text(
                DELETE_PACK_SUCCESS_MESSAGE.format(sticker_set)
            )
            await log_info("{}: deleted pack {}".format(update.effective_user.name, sticker_set), update.get_bot())
        else:
            await update.message.reply_text(DELETE_PACK_CONFIRMATION_MESSAGE, parse_mode=ParseMode.HTML)
            return CONFIRM_DELETE
    except BadRequest as e:
        await update.message.reply_text(PACK_NOT_FOUND_MESSAGE)
    context.user_data.pop("operation")
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
