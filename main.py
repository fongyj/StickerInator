from dotenv import load_dotenv
import logging
import os

load_dotenv()

from telegram import __version__ as TG_VER
import conversation.new_pack_conv as new_pack
import conversation.del_pack_conv as delete_pack
import conversation.del_sticker_conv as delete_sticker
import conversation.add_sticker_conv as add_sticker
import conversation.start_command as start
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
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, ApplicationHandlerStop

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

handlers_list = [start.get_start_command(), new_pack.get_new_pack_conv(), add_sticker.get_add_sticker_conv(), delete_pack.delete_pack_conv(), delete_sticker.delete_sticker_conv()]

command_info = [
    BotCommand("newpack", "Creates a new stickerpack"),
    BotCommand("addsticker", "Adds a sticker"),
    BotCommand("delsticker", "Deletes a sticker"),
    BotCommand("delpack", "Deletes a stickerpack"),
    BotCommand("help", "Gets info on the bot"),
    BotCommand("cancel", "Cancels current operation"),
]

async def post_init(application: Application) -> None:
    bot = application.bot
    await bot.set_my_commands(commands=command_info)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token = os.environ.get("BOT_TOKEN")
    application = Application.builder().token(token).post_init(post_init).build()

    application.add_handlers(handlers_list)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()