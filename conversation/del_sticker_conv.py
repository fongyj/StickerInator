from dotenv import load_dotenv
import logging

load_dotenv()

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram.error import BadRequest

SELECTING_PACK, CONFIRM_DELETE = map(chr, range(2))

async def delete_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("{}: delete sticker".format(update.effective_user.name))
    await update.message.reply_text("Please send the sticker you wish to delete")
    return SELECTING_PACK

async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        bot = update.get_bot()
        context.user_data["sticker"] = update.message.sticker
        sticker_set = context.user_data["sticker"].set_name
        sticker_set_info = await bot.get_sticker_set(sticker_set)

        # Iterate through the stickers in the sticker set
        for sticker_info in sticker_set_info.stickers:
            if context.user_data["sticker"].file_id == sticker_info.file_id:
                if len(sticker_set_info.stickers) == 1:
                    context.user_data["last"] = True
                    await update.message.reply_text("This is your last sticker. Deleting this will delete the sticker pack. Are you sure? Reply with yes")
                else:
                    context.user_data["last"] = False
                    await update.message.reply_text("Confirm delete sticker? Reply with yes")
                return CONFIRM_DELETE

        # If the sticker wasn't found in the set
        await update.message.reply_text("Sticker not found in the sticker set.")
    except BadRequest as e:
        await update.message.reply_text("No such sticker/stickerset. Cancelling operation")
    return ConversationHandler.END


async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.text.lower() == "yes":
            bot = update.get_bot()
            sticker_set = context.user_data["sticker"].set_name
            sticker = context.user_data["sticker"].file_id
            if context.user_data["last"]:
                await bot.delete_sticker_set(sticker_set)
                await update.message.reply_text(f"{sticker_set} deleted")
            else: 
                await bot.delete_sticker_from_set(sticker)
                await update.message.reply_text(f"Sticker deleted from {sticker_set}")
                logging.info("{}: deleted sticker from {}".format(update.effective_user.name, sticker_set))
        else:
            await update.message.reply_text("Please reply yes to confirm deletion, or do /cancel to cancel operation")
            return CONFIRM_DELETE
    except BadRequest as e:
        await update.message.reply_text("No such sticker/stickerset. Cancelling operation")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Invalid, command cancelled")
    return ConversationHandler.END

def delete_sticker_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("delsticker", delete_pack)],
        states={
            SELECTING_PACK: [MessageHandler(filters.Sticker.ALL, select_pack)],
            CONFIRM_DELETE: [MessageHandler(filters.TEXT, confirm_delete)],
            },
        fallbacks=[MessageHandler(filters.ALL, cancel)]
    )
