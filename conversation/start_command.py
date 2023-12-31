import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from conversation.messages import send_message, HELP_MESSAGE


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{}: start".format(update.effective_user.name))
    await send_message(update, HELP_MESSAGE)


def get_start_command():
    return CommandHandler("start", start)
