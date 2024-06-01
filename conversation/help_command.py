from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from conversation.messages import HELP_MESSAGE
from conversation.utils import send_message, log_info


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await log_info("{}: help".format(update.effective_user.name), update.get_bot())
    await send_message(update, HELP_MESSAGE)


def get_help_command():
    return CommandHandler("help", help)
