from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from conversation.messages import CANCEL_MESSAGE, NO_COMMAND_TO_CANCEL_MESSAGE
from conversation.utils import log_info


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    if "operation" not in context.user_data:
        await update.message.reply_text(NO_COMMAND_TO_CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove())
        await log_info("{}: cancelled without operation", update.get_bot())
    else:
        operation = context.user_data.pop("operation")
        await update.message.reply_text(CANCEL_MESSAGE.format(operation), reply_markup=ReplyKeyboardRemove())
        await log_info(
            "{}: cancelled operation {}".format(
                update.effective_user.name, operation
            ),
            update.get_bot()
        )
    return ConversationHandler.END
