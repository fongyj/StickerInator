from dotenv import load_dotenv
import os
import emoji
import requests
from io import BytesIO

load_dotenv()

from warnings import filterwarnings
from telegram import Update, InputSticker
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
from processing.video import VideoProcessor
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
    NEXT_STICKER_MESSAGE,
    CREATE_PACK_SUCCESS_MESSAGE,
    VIDEO_PROCESSING_MESSAGE,
    EMPTY_PACK_MESSAGE,
    PACK_LIMIT_REACHED_MESSAGE,
    SIZE_LIMIT_REACHED_MESSAGE,
    STICKER_NOT_SUPPORTED,
    DOWNLOAD_FAILED_IMAGE,
    DOWNLOAD_FAILED_VIDEO,
)
from conversation.utils import done_button, log_info, type_button

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
    await log_info("{}: create pack".format(update.effective_user.name), update.get_bot())
    
    async def final_state(update, context):
        await update.callback_query.message.reply_text(PACK_TITLE_MESSAGE)
        return SELECTING_TITLE

    context.user_data["final_state"] = final_state
    context.user_data["stickers"] = list()
    context.user_data["operation"] = "create pack"
    await update.message.reply_text(PACK_TYPE_MESSAGE, reply_markup=type_button())
    context.user_data["sticker_count"] = 0
    return SELECTING_TYPE


async def select_type(update: Update, context: CallbackContext):
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


async def select_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pack_type = context.user_data["type"]
    query = update.callback_query
    data = query.data if query else None
    sticker_count = context.user_data["sticker_count"]

    if data and data.lower() == "done" and sticker_count > 0:
        return await context.user_data["final_state"](update, context)
    elif data and data.lower() == "done":
        await query.message.reply_text(EMPTY_PACK_MESSAGE)
        return SELECTING_STICKER
    elif pack_type == StickerFormat.STATIC:
        return await select_image_sticker(update, context)
    elif pack_type == StickerFormat.VIDEO:
        return await select_video_sticker(update, context)


async def select_image_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker_count = context.user_data["sticker_count"]
    if sticker_count >= MAX_STATIC_STICKER:
        # too many stickers
        await update.message.reply_text(PACK_LIMIT_REACHED_MESSAGE.format("image", MAX_STATIC_STICKER))
        await update.message.reply_text(NEXT_STICKER_MESSAGE, reply_markup=done_button())
        return SELECTING_STICKER
    elif update.message.sticker:
        # user sent a sticker
        if update.message.sticker.is_animated or update.message.sticker.is_video:
            if sticker_count == 0:
                await update.message.reply_text(IMAGE_STICKER_MESSAGE)
            else:
                await update.message.reply_text(NEXT_STICKER_MESSAGE, reply_markup=done_button())
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
            await update.message.reply_text(NEXT_STICKER_MESSAGE, reply_markup=done_button())
            return SELECTING_STICKER
        else:
            await update.message.reply_text(DOWNLOAD_FAILED_IMAGE)

    elif update.message.photo:
        # user sent a photo
        file = await update.message.photo[-1].get_file()
    elif update.message.document and update.message.document.mime_type.startswith(
        "image"
    ):
        # user sent a file
        file = await update.message.document.get_file()
    else:
        # user did not send anything valid
        if sticker_count == 0:
            await update.message.reply_text(IMAGE_STICKER_MESSAGE)
        else:
            await update.message.reply_text(NEXT_STICKER_MESSAGE, reply_markup=done_button())
        return SELECTING_STICKER

    await log_info(
        "{}: uploaded image sticker {}".format(
            update.effective_user.name, file.file_id
        ),
        update.get_bot()
    )

    if file.file_size > MAX_FILE_SIZE:
        await log_info(
            "{}: file size limit reached {}".format(
                update.effective_user.name, file.file_size
            ),
            update.get_bot()
        )
        await update.message.reply_text(SIZE_LIMIT_REACHED_MESSAGE)
        return SELECTING_STICKER
    processed_sticker = process_image(file.file_path)
    context.user_data["sticker"] = processed_sticker
    context.user_data["sticker_count"] += 1
    await update.message.reply_text(STICKER_EMOJI_MESSAGE)
    return SELECTING_EMOJI


async def select_video_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker_count = context.user_data["sticker_count"]
    remove_bg = False
    if sticker_count >= MAX_VIDEO_STICKER:
        # too many stickers
        await update.message.reply_text(PACK_LIMIT_REACHED_MESSAGE.format("video", MAX_VIDEO_STICKER))
        await update.message.reply_text(NEXT_STICKER_MESSAGE, reply_markup=done_button())
        return SELECTING_STICKER
    elif update.message.sticker:
        # user sent a sticker
        if update.message.sticker.is_animated:
            await update.message.reply_text(STICKER_NOT_SUPPORTED)
            return SELECTING_STICKER
        if not update.message.sticker.is_video:
            if sticker_count == 0:
                await update.message.reply_text(VIDEO_STICKER_MESSAGE)
            else:
                await update.message.reply_text(NEXT_STICKER_MESSAGE, reply_markup=done_button())
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
            await update.message.reply_text(NEXT_STICKER_MESSAGE, reply_markup=done_button())
            return SELECTING_STICKER
        else:
            await update.message.reply_text(DOWNLOAD_FAILED_VIDEO)
            return SELECTING_STICKER
    elif update.message.video:
        # user sent a video
        file = await update.message.video.get_file()
    elif update.message.document and update.message.document.mime_type.startswith(
        "video"
    ):
        # user sent a file
        file = await update.message.document.get_file()
    elif update.message.video_note:
        # user sent a tele bubble
        file = await update.message.video_note.get_file()
        remove_bg = True
    else:
        # user did not send anything valid
        if sticker_count == 0:
            await update.message.reply_text(VIDEO_STICKER_MESSAGE)
        else:
            await update.message.reply_text(NEXT_STICKER_MESSAGE, reply_markup=done_button())
        return SELECTING_STICKER
    await log_info(
        "{}: uploaded video sticker {}".format(
            update.effective_user.name, file.file_id
        ),
        update.get_bot()
    )
    if file.file_size > MAX_FILE_SIZE:
        await log_info(
            "{}: file size limit reached {}".format(
                update.effective_user.name, file.file_size
            ),
            update.get_bot()
        )
        await update.message.reply_text(SIZE_LIMIT_REACHED_MESSAGE)
        return SELECTING_STICKER
    processor = VideoProcessor(file, remove_bg=remove_bg)
    context.user_data["processor"] = processor
    await processor.get_video()
    await update.message.reply_text(
        VIDEO_CROP_MESSAGE.format(processor.duration), parse_mode=ParseMode.HTML
    )
    return SELECTING_DURATION


async def select_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crop = update.message.text
    await log_info("{}: selected video crop {}".format(update.effective_user.name, crop), update.get_bot())
    duration = context.user_data["processor"].duration
    bot = update.get_bot()
    if crop.lower() == "ok" and duration > 3:
        await update.message.reply_text(VIDEO_TOO_LONG_MESSAGE)
        return SELECTING_DURATION
    elif crop.lower() == "ok":
        await bot.send_message(update.effective_chat.id, VIDEO_PROCESSING_MESSAGE)
        context.user_data["sticker"] = context.user_data["processor"].process_video()
    else:
        start_min, start_sec, crop_duration = context.user_data["processor"].parse_crop(
            crop
        )
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
    await log_info(
        "{}: selected emoji {}".format(update.effective_user.name, sticker_emoji),
        update.get_bot()
    )
    await update.message.reply_text(NEXT_STICKER_MESSAGE, reply_markup=done_button())
    return SELECTING_STICKER


async def select_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await log_info(
        "{}: selected {} as sticker pack title".format(
            update.effective_user.name, update.message.text
        ),
        update.get_bot()
    )
    context.user_data["title"] = update.message.text
    await update.message.reply_text(PACK_NAME_MESSAGE)
    return SELECTING_NAME


async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await log_info(
        "{}: selected {} as sticker pack name".format(
            update.effective_user.name, update.message.text
        ),
        update.get_bot()
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
            write_timeout=None
        )
        await update.message.reply_text(CREATE_PACK_SUCCESS_MESSAGE.format(name))
        await log_info(
            "{}: created sticker pack {}".format(update.effective_user.name, name),
            update.get_bot()
        )
        return ConversationHandler.END
    except TelegramError as te:
        await update.message.reply_text(te.message)
        await update.message.reply_text(PACK_NAME_MESSAGE)
        await log_info(
            "{}: error creating pack {}".format(update.effective_user.name, te.message),
            update.get_bot()
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
                CallbackQueryHandler(select_type, pattern="^image$|^video$"),
            ],
            SELECTING_STICKER: [
                CallbackQueryHandler(select_sticker),
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
