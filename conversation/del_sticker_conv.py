import os

from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.constants import ParseMode
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
    PACK_NOT_FOUND_MESSAGE,
    DELETE_PACK_SUCCESS_MESSAGE,
    DELETE_STICKER_SUCCESS_MESSAGE,
    INVALID_PACK_MESSAGE,
    ACTIVE_COMMAND_MESSAGE,
)
from conversation.utils import log_info
from conversation.cancel_command import cancel

SELECTING_PACK, CONFIRM_DELETE = map(chr, range(2))


async def delete_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'operation' in context.user_data:
        await update.message.reply_text(ACTIVE_COMMAND_MESSAGE.format(context.user_data['operation']))
        return ConversationHandler.END

    await log_info("{}: delete sticker".format(update.effective_user.name), update.get_bot())
    context.user_data["operation"] = "delete sticker"
    context.user_data["conversation_key"] = (update._effective_chat.id, update._effective_user.id)
    await update.message.reply_text(DELETE_STICKER_MESSAGE)
    return SELECTING_PACK


async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        bot = update.get_bot()
        context.user_data["sticker"] = update.message.sticker
        sticker_set = context.user_data["sticker"].set_name
        await log_info("{}: selected sticker pack {}".format(update.effective_user.name, sticker_set), update.get_bot())
        if not sticker_set.endswith("_by_" + os.environ.get("BOT_NAME")):
            await update.message.reply_text(INVALID_PACK_MESSAGE)
            await update.message.reply_text(DELETE_STICKER_MESSAGE)
            return SELECTING_PACK
        sticker_set_info = await bot.do_api_request("get_sticker_set", {"name": sticker_set})

        # Iterate through the stickers in the sticker set
        for sticker_info in sticker_set_info["stickers"]:
            if context.user_data["sticker"].file_id == sticker_info["file_id"]:
                if len(sticker_set_info["stickers"]) == 1:
                    context.user_data["last"] = True
                    await update.message.reply_text(LAST_STICKER_MESSAGE, parse_mode=ParseMode.HTML)
                else:
                    context.user_data["last"] = False
                    await update.message.reply_text(DELETE_STICKER_CONFIRMATION_MESSAGE, parse_mode=ParseMode.HTML)
                return CONFIRM_DELETE

        # If the sticker wasn't found in the set
        await update.message.reply_text(STICKER_NOT_FOUND_MESSAGE)
    except BadRequest as e:
        await update.message.reply_text(PACK_NOT_FOUND_MESSAGE)
    context.user_data.pop("operation")
    return ConversationHandler.END


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.text.lower() == "delete sticker":
            bot = update.get_bot()
            sticker_set = context.user_data["sticker"].set_name
            sticker = context.user_data["sticker"].file_id
            if context.user_data["last"]:
                await bot.delete_sticker_set(sticker_set)
                await update.message.reply_text(DELETE_PACK_SUCCESS_MESSAGE.format(sticker_set))
                await log_info("{}: deleted pack {}".format(update.effective_user.name, sticker_set), update.get_bot())
            else:
                await bot.delete_sticker_from_set(sticker)
                await update.message.reply_text(DELETE_STICKER_SUCCESS_MESSAGE.format(sticker_set))
                await log_info("{}: deleted sticker from {}".format(update.effective_user.name, sticker_set), update.get_bot())
        else:
            await update.message.reply_text(DELETE_STICKER_CONFIRMATION_MESSAGE, parse_mode=ParseMode.HTML)
            return CONFIRM_DELETE
    except BadRequest as e:
        await update.message.reply_text(PACK_NOT_FOUND_MESSAGE)
    context.user_data.pop("operation")
    return ConversationHandler.END


def delete_sticker_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("delsticker", delete_sticker)],
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
