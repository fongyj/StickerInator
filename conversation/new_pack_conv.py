import logging

from telegram import Update, InputSticker
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram.constants import StickerFormat

from processing.image import process_image
from processing.video import VideoProcessor, parse_crop

SELECTING_NAME, SELECTING_TITLE, SELECTING_TYPE, SELECTING_STICKER, SELECTING_DURATION, SELECTING_EMOJI = map(chr, range(6))

async def new_pack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("{}: create sticker pack".format(update.effective_user.name))
    await update.message.reply_text("Please reply with sticker pack name")
    return SELECTING_NAME

async def select_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{}: selected {} as sticker pack name".format(update.effective_user.name, update.message.text)) # verify that the pack name is valid?
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Please reply with sticker pack title")
    return SELECTING_TITLE

async def select_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{}: selected {} as sticker pack title".format(update.effective_user.name, update.message.text))
    context.user_data["title"] = update.message.text
    await update.message.reply_text("Please reply with sticker pack type: IMAGE or VIDEO")
    return SELECTING_TYPE

async def select_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{}: selected {} as sticker pack type".format(update.effective_user.name, update.message.text.upper()))
    pack_type = update.message.text.upper()
    if pack_type == "IMAGE":
        context.user_data["type"] = StickerFormat.STATIC
        context.user_data["stickers"] = list()
        await update.message.reply_text("Please send image sticker")
    elif pack_type == "VIDEO":
        context.user_data["type"] = StickerFormat.VIDEO
        context.user_data["stickers"] = list()
        await update.message.reply_text("Please send video sticker")
    else:
        await update.message.reply_text("Please reply with IMAGE or VIDEO")
        return SELECTING_TYPE
    return SELECTING_STICKER

async def select_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pack_type = context.user_data["type"]
    text = update.message.text
    bot = update.get_bot()
    if text and text.upper() == "DONE":
        name = context.user_data["name"] + "_by_StickerInatorBot" # this is required in the name of a stickerpack created by a bot
        await bot.create_new_sticker_set(update.effective_user.id,
                                         name,
                                         context.user_data["title"], 
                                         stickers=context.user_data["stickers"], 
                                         sticker_format=context.user_data["type"])
        await update.message.reply_text("Sticker pack created: https://t.me/addstickers/{}".format(name))
        logging.info("{}: created sticker pack {}".format(update.effective_user.name, name))
        return ConversationHandler.END
    elif text:
        await update.message.reply_text("Please send another sticker OR reply with DONE when finished")
        return SELECTING_STICKER

    if pack_type == StickerFormat.STATIC:
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
        elif update.message.document and update.message.document.mime_type.startswith("image"):
            file = await update.message.document.get_file()
        else:
            await update.message.reply_text("Please send an image")
            return SELECTING_STICKER
        logging.info("{}: uploaded image sticker {}".format(update.effective_user.name, file.file_path))
        processed_sticker = process_image(file.file_path)
        context.user_data["sticker"] = processed_sticker
        await update.message.reply_text("Please send a emoji for the sticker")
        return SELECTING_EMOJI
    
    elif pack_type == StickerFormat.VIDEO:
        if update.message.video:
            file = await update.message.video.get_file()
        elif update.message.document and update.message.document.mime_type.startswith("video"):
            file = await update.message.document.get_file()
        elif update.message.video_note:
            file = await update.message.video_note.get_file()
        else:
            await update.message.reply_text("Please send a video")
            return SELECTING_STICKER
        logging.info("{}: uploaded video sticker {}".format(update.effective_user.name, file.file_path))
        processor = VideoProcessor(file)
        context.user_data["processor"] = processor
        await processor.get_video()
        context.user_data["duration"] = processor.get_duration()
        await update.message.reply_text(f"Video duration is {processor.get_duration()} seconds\n"+
                                        "Crop video by replying with start time followed by duration \"mm:ss.SSS s.SSS\" (m for minutes, s for seconds, S for fraction of a second)\n"+
                                        "Reply with \"OK\" if no video cropping is needed\n" +
                                        "Note that maximum duration for a video sticker is 3 seconds")
        return SELECTING_DURATION

async def select_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crop = update.message.text
    logging.info("{}: selected video crop {}".format(update.effective_user.name, crop))
    duration = context.user_data["duration"]
    if crop.upper() == "OK" and duration > 3:
        await update.message.reply_text("Video duration is too long, crop video by replying with start time followed by duration\"mm:ss.SSS s.SSS\" (m for minutes, s for seconds, S for fraction of a second)")
        return SELECTING_DURATION
    elif crop.upper() == "OK":
        context.user_data["sticker"] = context.user_data["processor"].process_video()
        await update.message.reply_text("Please send a emoji for the sticker")
        return SELECTING_EMOJI
    else:
        start_min, start_sec, crop_duration = parse_crop(crop)
        if start_min == None:
            await update.message.reply_text("Invalid start timestamp and duration, reply with start time followed by duration\"mm:ss.SSS s.SSS\" (m for minutes, s for seconds, S for fraction of a second)")
            return SELECTING_DURATION
        context.user_data["sticker"] = context.user_data["processor"].process_video(start_min, start_sec, crop_duration)
        await update.message.reply_text("Please send a emoji for the sticker")
        return SELECTING_EMOJI

async def select_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker = context.user_data["sticker"]
    context.user_data["stickers"].append(InputSticker(sticker, [update.message.text])) # verify the user sent an emoji?
    logging.info("{}: selected emoji {}".format(update.effective_user.name, update.message.text))
    await update.message.reply_text("Please send another sticker OR reply with DONE when finished")
    return SELECTING_STICKER

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{}: invalid, command cancelled {}".format(update.effective_user.name, update.message.text))
    await update.message.reply_text("Invalid, command cancelled") # implement a cancel command
    return ConversationHandler.END

def get_new_pack_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("newpack", new_pack)],
        states={
            SELECTING_NAME: [MessageHandler(filters.TEXT, select_name)],
            SELECTING_TITLE: [MessageHandler(filters.TEXT, select_title)],
            SELECTING_TYPE: [MessageHandler(filters.TEXT, select_type)],
            SELECTING_STICKER: [MessageHandler(filters.ALL, select_sticker)],
            SELECTING_DURATION: [MessageHandler(filters.TEXT, select_duration)],
            SELECTING_EMOJI: [MessageHandler(filters.TEXT, select_emoji)]
            },
        fallbacks=[MessageHandler(filters.ALL, cancel)]
    )
