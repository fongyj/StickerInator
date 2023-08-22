from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from conversation.messages import send_message, HELP_MESSAGE


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_message(update, HELP_MESSAGE)


def get_start_command():
    return CommandHandler("start", help)


def get_help_command():
    return CommandHandler("help", help)
