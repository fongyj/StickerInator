from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Operation Cancelled", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END
