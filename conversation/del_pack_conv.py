from dotenv import load_dotenv
import logging

load_dotenv()

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram.error import BadRequest

SELECTING_PACK, CONFIRM_DELETE = map(chr, range(2))

async def delete_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("{}: delete pack".format(update.effective_user.name))
    await update.message.reply_text("Please send a sticker from your sticker set")
    return SELECTING_PACK

async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sticker"] = update.message.sticker
    await update.message.reply_text("Confirm delete pack? Reply with yes")
    return CONFIRM_DELETE

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.text.lower() == "yes":
            bot = update.get_bot()
            sticker_set = context.user_data["sticker"].set_name
            await bot.delete_sticker_set(sticker_set)
            await update.message.reply_text(f"Sticker pack {sticker_set} deleted")
            logging.info("{}: deleted pack {}".format(update.effective_user.name, sticker_set))
        else:
            await update.message.reply_text("Please reply yes to confirm deletion, or do /cancel to cancel operation")
            return CONFIRM_DELETE
    except BadRequest as e:
        await update.message.reply_text("No such sticker/stickerset. Cancelling operation")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Operation Cancelled", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def delete_pack_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("delpack", delete_pack)],
        states={
            SELECTING_PACK: [MessageHandler(filters.Sticker.ALL, select_pack)],
            CONFIRM_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_delete)],
            },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
