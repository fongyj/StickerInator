from dotenv import load_dotenv
import logging
import os
import html
import json
import traceback

load_dotenv()

from telegram import __version__ as TG_VER
from telegram.constants import ParseMode

import conversation.new_pack_conv as new_pack
import conversation.del_pack_conv as delete_pack
import conversation.del_sticker_conv as delete_sticker
import conversation.add_sticker_conv as add_sticker
import conversation.start_command as start
import conversation.help_command as help
import conversation.reset_command as reset
from conversation.utils import log_info
from conversation.messages import UNHANDLED_STICKERINATOR_ERROR_MESSAGE

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
from telegram.ext import Application, ContextTypes


from conversation.messages import (
    NEW_PACK_HELP,
    ADD_STICKER_HELP,
    DEL_STICKER_HELP,
    DEL_PACK_HELP,
    HELP_HELP,
    CANCEL_HELP,
    RESET_HELP
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
os.makedirs("logs", exist_ok=True)
file_handler = logging.FileHandler("logs/stickerinator.log", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logging.getLogger().addHandler(file_handler)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)

start_command = start.get_start_command()
new_pack_command = new_pack.get_new_pack_conv()
add_sticker_command = add_sticker.get_add_sticker_conv()
delete_pack_command = delete_pack.delete_pack_conv()
delete_sticker_command = delete_sticker.delete_sticker_conv()
help_command = help.get_help_command()
reset_command = reset.get_reset_command([new_pack_command, add_sticker_command, delete_pack_command, delete_sticker_command])

handlers_list = [
    start_command,
    new_pack_command,
    add_sticker_command,
    delete_pack_command,
    delete_sticker_command,
    help_command,
    reset_command
]

command_info = [
    BotCommand("newpack", NEW_PACK_HELP),
    BotCommand("addsticker", ADD_STICKER_HELP),
    BotCommand("delsticker", DEL_STICKER_HELP),
    BotCommand("delpack", DEL_PACK_HELP),
    BotCommand("help", HELP_HELP),
    BotCommand("cancel", CANCEL_HELP),
    BotCommand("reset", RESET_HELP)
]


async def post_init(application: Application) -> None:
    bot = application.bot
    await bot.set_my_commands(commands=command_info)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "Sticker-inator encountered an unhandled exception\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
    )
    stack = (
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    bot = update.get_bot()
    logging.error(tb_string)
    await bot.send_message(os.environ.get("LOG_ID"), message, parse_mode=ParseMode.HTML)
    await bot.send_message(os.environ.get("LOG_ID"), stack, parse_mode=ParseMode.HTML)
    await bot.send_message(update.effective_chat.id, UNHANDLED_STICKERINATOR_ERROR_MESSAGE)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token = os.environ.get("BOT_TOKEN_STICKERINATOR")
    application = Application.builder().token(token).post_init(post_init).build()

    application.add_handlers(handlers_list)
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
