from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler
)

from conversation.messages import RESET_MESSAGE
from conversation.utils import log_info
from typing import List

def reset(command_handlers: List[ConversationHandler]):
    async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Resets all conversations and clear users data"""
        await log_info("{}: reset".format(update.effective_user.name), update.get_bot())
        context.user_data.clear()
        for handlers in command_handlers:
            handlers._update_state(ConversationHandler.END, handlers._get_key(update))
        await update.message.reply_text(RESET_MESSAGE, reply_markup=ReplyKeyboardRemove())
    return reset

def get_reset_command(command_handlers):
    return CommandHandler("reset", reset(command_handlers))
