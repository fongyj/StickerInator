import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from conversation.messages import CANCEL_MESSAGE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
    logging.info(
        "{}: cancelled operation {}".format(
            update.effective_user.name, context.user_data["operation"]
        )
    )
    return ConversationHandler.END
