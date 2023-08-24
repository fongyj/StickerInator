from dotenv import load_dotenv
import logging
import os
from dataclasses import dataclass
import asyncio
from http import HTTPStatus

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

load_dotenv()

from telegram import __version__ as TG_VER
import conversation.new_pack_conv as new_pack
import conversation.del_pack_conv as delete_pack
import conversation.del_sticker_conv as delete_sticker
import conversation.add_sticker_conv as add_sticker
import conversation.start_command as start
import conversation.help_command as help

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
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    ContextTypes,
    ExtBot,
    TypeHandler,
)

from conversation.messages import (
    NEW_PACK_HELP,
    ADD_STICKER_HELP,
    DEL_STICKER_HELP,
    DEL_PACK_HELP,
    HELP_HELP,
    CANCEL_HELP,
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

handlers_list = [
    start.get_start_command(),
    new_pack.get_new_pack_conv(),
    add_sticker.get_add_sticker_conv(),
    delete_pack.delete_pack_conv(),
    delete_sticker.delete_sticker_conv(),
    help.get_help_command(),
]


command_info = [
    BotCommand("newpack", NEW_PACK_HELP),
    BotCommand("addsticker", ADD_STICKER_HELP),
    BotCommand("delsticker", DEL_STICKER_HELP),
    BotCommand("delpack", DEL_PACK_HELP),
    BotCommand("help", HELP_HELP),
    BotCommand("cancel", CANCEL_HELP),
]


@dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type"""

    user_id: int
    payload: str


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)


async def webhook_update(update: WebhookUpdate, context: CustomContext) -> None:
    """Callback that handles the custom updates."""
    chat_member = await context.bot.get_chat_member(
        chat_id=update.user_id, user_id=update.user_id
    )
    payloads = context.user_data.setdefault("payloads", [])
    payloads.append(update.payload)
    combined_payloads = "</code>\n• <code>".join(payloads)
    text = (
        f"The user {chat_member.user.mention_html()} has sent a new payload. "
        f"So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>"
    )
    await context.bot.send_message(
        chat_id=context.bot_data["admin_chat_id"], text=text, parse_mode=ParseMode.HTML
    )


async def post_init(application: Application) -> None:
    bot = application.bot
    await bot.set_my_commands(commands=command_info)


async def main() -> None:
    """Start the bot."""
    url = "https://stickerinator.pages.dev/"
    admin_chat_id = 123456
    port = 8000

    context_types = ContextTypes(context=CustomContext)
    # Here we set updater to None because we want our custom webhook server to handle the updates
    # and hence we don't need an Updater instance
    token = os.environ.get("BOT_TOKEN")
    application = (
        Application.builder()
        .token(token)
        .updater(None)
        .context_types(context_types)
        .build()
    )
    # save the values in `bot_data` such that we may easily access them in the callbacks
    application.bot_data["url"] = url
    application.bot_data["admin_chat_id"] = admin_chat_id

    # register handlers
    application.add_handlers(handlers_list)
    application.add_handler(TypeHandler(type=WebhookUpdate, callback=webhook_update))

    # Pass webhook settings to telegram
    await application.bot.set_webhook(
        url=f"{url}/telegram", allowed_updates=Update.ALL_TYPES
    )

    # Set up webserver
    async def telegram(request: Request) -> Response:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        await application.update_queue.put(
            Update.de_json(data=await request.json(), bot=application.bot)
        )
        return Response()

    async def custom_updates(request: Request) -> PlainTextResponse:
        """
        Handle incoming webhook updates by also putting them into the `update_queue` if
        the required parameters were passed correctly.
        """
        try:
            user_id = int(request.query_params["user_id"])
            payload = request.query_params["payload"]
        except KeyError:
            return PlainTextResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content="Please pass both `user_id` and `payload` as query parameters.",
            )
        except ValueError:
            return PlainTextResponse(
                status_code=HTTPStatus.BAD_REQUEST,
                content="The `user_id` must be a string!",
            )

        await application.update_queue.put(
            WebhookUpdate(user_id=user_id, payload=payload)
        )
        return PlainTextResponse("Thank you for the submission! It's being forwarded.")

    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram, methods=["POST"]),
            Route("/submitpayload", custom_updates, methods=["POST", "GET"]),
        ]
    )
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=starlette_app,
            port=port,
            use_colors=False,
            host="127.0.0.1",
        )
    )

    # Run application and webserver together
    async with application:
        await application.start()
        await webserver.serve()
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())
