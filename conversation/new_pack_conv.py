from dotenv import load_dotenv
import logging
import os
import emoji
import requests
from io import BytesIO

load_dotenv()

from warnings import filterwarnings
from telegram import Update, InputSticker, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from telegram.constants import StickerFormat
from telegram.warnings import PTBUserWarning

from processing.image import process_image
from processing.video import VideoProcessor, parse_crop
from conversation.messages import (
    PACK_NAME_MESSAGE,
    PACK_TITLE_MESSAGE,
    PACK_TYPE_MESSAGE,
    IMAGE_STICKER_MESSAGE,
    VIDEO_STICKER_MESSAGE,
    STICKER_EMOJI_MESSAGE,
    VIDEO_TOO_LONG_MESSAGE,
    VIDEO_CROP_MESSAGE,
    INVALID_VIDEO_DURATION_MESSAGE,
    ADD_NEXT_STICKER_MESSAGE,
    CREATE_PACK_SUCCESS_MESSAGE,
    VIDEO_PROCESSING_MESSAGE,
    PACK_LIMIT_REACHED_MESSAGE,
    SIZE_LIMIT_REACHED_MESSAGE,
    STICKER_NOT_SUPPORTED,
    DOWNLOAD_FAILED_IMAGE,
    DOWNLOAD_FAILED_VIDEO,
)

(
    SELECTING_TYPE,
    SELECTING_STICKER,
    SELECTING_DURATION,
    SELECTING_EMOJI,
    SELECTING_NAME,
    SELECTING_TITLE,
) = map(chr, range(6))
from conversation.cancel_command import cancel

MAX_STATIC_STICKER = 120
MAX_VIDEO_STICKER = 50
MAX_FILE_SIZE = 50000000  # 50mb


async def new_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("{}: create pack".format(update.effective_user.name))

    async def final_state(update, context):
        await update.message.reply_text(PACK_TITLE_MESSAGE)
        return SELECTING_TITLE

    context.user_data["final_state"] = final_state
    context.user_data["stickers"] = list()
    context.user_data["operation"] = "create pack"
    keyboard = [
        [
            InlineKeyboardButton("IMAGE", callback_data="image"),
            InlineKeyboardButton("VIDEO", callback_data="video"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(PACK_TYPE_MESSAGE, reply_markup=reply_markup)
    context.user_data["sticker_count"] = 0
    return SELECTING_TYPE


async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data == "image":
        context.user_data["type"] = StickerFormat.STATIC
        await query.message.reply_text(IMAGE_STICKER_MESSAGE)
        return SELECTING_STICKER
    elif data == "video":
        context.user_data["type"] = StickerFormat.VIDEO
        await query.message.reply_text(VIDEO_STICKER_MESSAGE)
        return SELECTING_STICKER


async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(
        "{}: selected {} as sticker pack type".format(
            update.effective_user.name, update.message.text.lower()
        )
    )
    pack_type = update.callback_query.data.lower()
    if pack_type == "image":
        context.user_data["type"] = StickerFormat.STATIC
        await update.message.reply_text(IMAGE_STICKER_MESSAGE)
    elif pack_type == "video":
        context.user_data["type"] = StickerFormat.VIDEO
        await update.message.reply_text(VIDEO_STICKER_MESSAGE)
    return SELECTING_STICKER


async def select_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pack_type = context.user_data["type"]
    text = update.message.text
    if text and text.lower() == "done":
        return await context.user_data["final_state"](update, context)

    if pack_type == StickerFormat.STATIC:
        return await select_image_sticker(update, context)
    elif pack_type == StickerFormat.VIDEO:
        return await select_video_sticker(update, context)


async def select_image_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["sticker_count"] >= MAX_STATIC_STICKER:
        await update.message.reply_text(
            PACK_LIMIT_REACHED_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2
        )
        return SELECTING_STICKER
    elif update.message.sticker:
        if update.message.sticker.is_animated or update.message.sticker.is_video:
            await update.message.reply_text(IMAGE_STICKER_MESSAGE)
            return SELECTING_STICKER

        bot = update.get_bot()
        file = await bot.get_file(update.message.sticker.file_id)
        file_path = file.file_path

        response = requests.get(file_path)

        if response.status_code == 200:
            sticker_file = BytesIO(response.content)

            context.user_data["stickers"].append(
                InputSticker(sticker_file, [update.message.sticker.emoji])
            )
            context.user_data["sticker_count"] += 1
            await update.message.reply_text(
                ADD_NEXT_STICKER_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2
            )
            return SELECTING_STICKER
        else:
            await update.message.reply_text(DOWNLOAD_FAILED_IMAGE)

    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
    elif update.message.document and update.message.document.mime_type.startswith(
        "image"
    ):
        file = await update.message.document.get_file()
    else:
        await update.message.reply_text(IMAGE_STICKER_MESSAGE)
        return SELECTING_STICKER
    logging.info(
        "{}: uploaded image sticker {}".format(
            update.effective_user.name, file.file_path
        )
    )

    if file.file_size > MAX_FILE_SIZE:
        logging.info(
            "{}: file size limit reached {}".format(
                update.effective_user.name, file.file_size
            )
        )
        await update.message.reply_text(SIZE_LIMIT_REACHED_MESSAGE)
        return SELECTING_STICKER
    processed_sticker = process_image(file.file_path)
    context.user_data["sticker"] = processed_sticker
    context.user_data["sticker_count"] += 1
    await update.message.reply_text(STICKER_EMOJI_MESSAGE)
    return SELECTING_EMOJI


async def select_video_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data["sticker_count"] >= MAX_VIDEO_STICKER:
        await update.message.reply_text(
            PACK_LIMIT_REACHED_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2
        )
        return SELECTING_STICKER
    elif update.message.sticker:
        if update.message.sticker.is_animated:
            await update.message.reply_text(STICKER_NOT_SUPPORTED)
            return SELECTING_STICKER
        if not update.message.sticker.is_video:
            await update.message.reply_text(VIDEO_STICKER_MESSAGE)
            return SELECTING_STICKER
        bot = update.get_bot()
        file = await bot.get_file(update.message.sticker.file_id)
        file_path = file.file_path

        response = requests.get(file_path)

        if response.status_code == 200:
            sticker_file = BytesIO(response.content)

            context.user_data["stickers"].append(
                InputSticker(sticker_file, [update.message.sticker.emoji])
            )
            context.user_data["sticker_count"] += 1
            await update.message.reply_text(
                ADD_NEXT_STICKER_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2
            )
            return SELECTING_STICKER
        else:
            await update.message.reply_text(DOWNLOAD_FAILED_VIDEO)
            return SELECTING_STICKER
    elif update.message.video:
        file = await update.message.video.get_file()
    elif update.message.document and update.message.document.mime_type.startswith(
        "video"
    ):
        file = await update.message.document.get_file()
    elif update.message.video_note:
        file = await update.message.video_note.get_file()
    else:
        await update.message.reply_text(VIDEO_STICKER_MESSAGE)
        return SELECTING_STICKER
    logging.info(
        "{}: uploaded video sticker {}".format(
            update.effective_user.name, file.file_path
        )
    )
    if file.file_size > MAX_FILE_SIZE:
        logging.info(
            "{}: file size limit reached {}".format(
                update.effective_user.name, file.file_size
            )
        )
        await update.message.reply_text(SIZE_LIMIT_REACHED_MESSAGE)
        return SELECTING_STICKER
    processor = VideoProcessor(file)
    context.user_data["processor"] = processor
    await processor.get_video()
    context.user_data["duration"] = processor.get_duration()
    await update.message.reply_text(
        VIDEO_CROP_MESSAGE.format(processor.get_duration()), parse_mode=ParseMode.HTML
    )
    return SELECTING_DURATION


async def select_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crop = update.message.text
    logging.info("{}: selected video crop {}".format(update.effective_user.name, crop))
    duration = context.user_data["duration"]
    bot = update.get_bot()
    if crop.lower() == "ok" and duration > 3:
        await update.message.reply_text(VIDEO_TOO_LONG_MESSAGE)
        return SELECTING_DURATION
    elif crop.lower() == "ok":
        await bot.send_message(update.effective_chat.id, VIDEO_PROCESSING_MESSAGE)
        context.user_data["sticker"] = context.user_data["processor"].process_video()
    else:
        duration = context.user_data["processor"].get_duration()
        start_min, start_sec, crop_duration = parse_crop(crop, duration)
        if start_min == None:
            await update.message.reply_text(INVALID_VIDEO_DURATION_MESSAGE)
            await update.message.reply_text(
                VIDEO_CROP_MESSAGE.format(duration), parse_mode=ParseMode.HTML
            )
            return SELECTING_DURATION
        await bot.send_message(update.effective_chat.id, VIDEO_PROCESSING_MESSAGE)
        context.user_data["sticker"] = context.user_data["processor"].process_video(
            start_min, start_sec, crop_duration
        )
    context.user_data["sticker_count"] += 1
    await update.message.reply_text(STICKER_EMOJI_MESSAGE)
    return SELECTING_EMOJI


async def select_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = context.user_data["sticker"]
    sticker_emoji = update.message.text
    if not emoji.is_emoji(sticker_emoji) or not len(sticker_emoji) == 1:
        await update.message.reply_text(STICKER_EMOJI_MESSAGE)
        return SELECTING_EMOJI
    context.user_data["stickers"].append(InputSticker(sticker, [sticker_emoji]))
    logging.info(
        "{}: selected emoji {}".format(update.effective_user.name, sticker_emoji)
    )
    await update.message.reply_text(
        ADD_NEXT_STICKER_MESSAGE, parse_mode=ParseMode.MARKDOWN_V2
    )
    return SELECTING_STICKER


async def select_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(
        "{}: selected {} as sticker pack title".format(
            update.effective_user.name, update.message.text
        )
    )
    context.user_data["title"] = update.message.text
    await update.message.reply_text(PACK_NAME_MESSAGE)
    return SELECTING_NAME


async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(
        "{}: selected {} as sticker pack name".format(
            update.effective_user.name, update.message.text
        )
    )
    context.user_data["name"] = update.message.text
    return await create_pack(update, context)


async def create_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = (
        context.user_data["name"] + "_by_" + os.environ.get("BOT_NAME")
    )  # this is required in the name of a stickerpack created by a bot
    bot = update.get_bot()
    try:
        await bot.create_new_sticker_set(
            update.effective_user.id,
            name,
            context.user_data["title"],
            stickers=context.user_data["stickers"],
            sticker_format=context.user_data["type"],
        )
        await update.message.reply_text(CREATE_PACK_SUCCESS_MESSAGE.format(name))
        logging.info(
            "{}: created sticker pack {}".format(update.effective_user.name, name)
        )
        return ConversationHandler.END
    except TelegramError as te:
        await update.message.reply_text(te.message)
        await update.message.reply_text(PACK_NAME_MESSAGE)
        logging.info(
            "{}: error creating pack {}".format(update.effective_user.name, te.message)
        )
        return SELECTING_NAME


def get_new_pack_conv():
    filterwarnings(
        action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
    )
    return ConversationHandler(
        entry_points=[CommandHandler("newpack", new_pack)],
        states={
            SELECTING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_name)
            ],
            SELECTING_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_title)
            ],
            SELECTING_TYPE: [
                CallbackQueryHandler(button_click, pattern="^image$|^video$"),
            ],
            SELECTING_STICKER: [
                MessageHandler(filters.ALL & ~filters.COMMAND, select_sticker)
            ],
            SELECTING_DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_duration)
            ],
            SELECTING_EMOJI: [
                MessageHandler(filters.ALL & ~filters.COMMAND, select_emoji)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
