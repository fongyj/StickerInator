import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import Update, InputSticker
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram.constants import StickerFormat

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

SELECTING_NAME, SELECTING_TITLE = map(chr, range(2))

async def new_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Create pack by {}".format(update.effective_user.name))
    await update.message.reply_text("Please reply with sticker pack name")
    return SELECTING_NAME

async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Please reply with sticker pack title")
    return SELECTING_TITLE

async def select_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = update.get_bot()
    user_id = update.effective_user.id
    name = context.user_data["name"] + "_by_StickerInatorBot" # this is required in the name of a stickerpack created by a bot
    title = update.message.text
    await bot.create_new_sticker_set(user_id, name, title, stickers=[InputSticker(open("sus_cat.PNG", "rb").read(), ["😀"])], sticker_format=StickerFormat.STATIC)
    await update.message.reply_text("Sticker pack created: https://t.me/addstickers/{}".format(name))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Invalid, command cancelled")
    return ConversationHandler.END

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    with open("token.txt", 'r') as f:
        token = f.readline()
    application = Application.builder().token(token).build()

    # new pack conversation:
    # 1. call newpack command
    # 2. user selects pack name
    # 3. user selects pack title
    new_pack_conv = ConversationHandler(
        entry_points=[CommandHandler("newpack", new_pack)],
        states={
            SELECTING_NAME: [MessageHandler(filters.TEXT, select_name)],
            SELECTING_TITLE: [MessageHandler(filters.TEXT, select_title)]},
        fallbacks=[MessageHandler(filters.ALL, cancel)]
    )
    application.add_handler(new_pack_conv)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()