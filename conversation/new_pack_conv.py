from dotenv import load_dotenv
import logging
import os

load_dotenv()

from telegram import Update, InputSticker
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram.constants import StickerFormat

SELECTING_NAME, SELECTING_TITLE = map(chr, range(2))

async def new_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Create pack by {}".format(update.effective_user.name))
    await update.message.reply_text("Please reply with sticker pack name")
    return SELECTING_NAME

async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Please reply with sticker pack title")
    return SELECTING_TITLE

async def select_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = update.get_bot()
    user_id = update.effective_user.id
    name = context.user_data["name"] + os.environ.get("BOT_NAME") # this is required in the name of a stickerpack created by a bot
    title = update.message.text
    await bot.create_new_sticker_set(user_id, name, title, stickers=[InputSticker(open("sus_cat.PNG", "rb").read(), ["😀"]), InputSticker(open("anya.png", "rb").read(), ["😀"])], sticker_format=StickerFormat.STATIC)
    await update.message.reply_text("Sticker pack created: https://t.me/addstickers/{}".format(name))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Invalid, command cancelled")
    return ConversationHandler.END

def get_new_pack_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("newpack", new_pack)],
        states={
            SELECTING_NAME: [MessageHandler(filters.TEXT, select_name)],
            SELECTING_TITLE: [MessageHandler(filters.TEXT, select_title)],
            },
        fallbacks=[MessageHandler(filters.ALL, cancel)]
    )
