from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

WELCOME_MESSAGE = "StickerInator is made to help you with creating stickerpacks with images, videos and telegram bubbles!\n\n"+\
    "Available commands:\n"+\
        "/newpack - Creates a new stickerpack\n"+\
            "/addsticker - Adds a sticker\n"+\
                "/delsticker - Deletes a sticker\n"+\
                    "/delpack - Deletes a stickerpack"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE)

def get_start_command():
    return CommandHandler("start", start)