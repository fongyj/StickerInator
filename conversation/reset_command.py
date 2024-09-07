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
        for handlers in command_handlers:
            if "conversation_key" in context.user_data:
                handlers._update_state(ConversationHandler.END, context.user_data["conversation_key"])
            handlers._update_state(ConversationHandler.END, handlers._get_key(update))
        context.user_data.clear()
        await update.message.reply_text(RESET_MESSAGE, reply_markup=ReplyKeyboardRemove())
    return reset

def get_reset_command(command_handlers):
    return CommandHandler("reset", reset(command_handlers))
