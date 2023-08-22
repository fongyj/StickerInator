import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from conversation.messages import send_message, HELP_MESSAGE


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{}: help".format(update.effective_user.name))
    await send_message(update, HELP_MESSAGE)


def get_help_command():
    return CommandHandler("help", help)
