import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram.constants import StickerFormat

from conversation.new_pack_conv import SELECTING_STICKER, SELECTING_DURATION, SELECTING_EMOJI
from conversation.new_pack_conv import select_sticker, select_duration, select_emoji

SELECTING_PACK = map(chr, range(7, 8))

async def new_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("{}: add sticker".format(update.effective_user.name))
    context.user_data["action"] = add_sticker
    context.user_data["stickers"] = list()
    await update.message.reply_text("Please send a sticker from your sticker set")
    return SELECTING_PACK

async def select_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_name = update.message.sticker.set_name
    logging.info("{}: selected sticker pack {}".format(update.effective_user.name, set_name))
    bot = update.get_bot()
    sticker_set = await bot.get_sticker_set(set_name)
    context.user_data["set_name"] = set_name
    if sticker_set.is_video:
        context.user_data["type"] = StickerFormat.VIDEO 
        await update.message.reply_text("Please send video sticker to be added")
    else:
        context.user_data["type"] = StickerFormat.STATIC 
        await update.message.reply_text("Please send image sticker to be added")
    return SELECTING_STICKER

async def add_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = update.get_bot()
    for sticker in context.user_data["stickers"]:
        await bot.add_sticker_to_set(update.effective_user.id,
                                    context.user_data["set_name"],
                                    sticker=sticker)
    await update.message.reply_text("Added stickers!")
    logging.info("{}: added sticker(s)".format(update.effective_user.name))

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("{}: invalid, command cancelled {}".format(update.effective_user.name, update.message.text))
    await update.message.reply_text("Invalid, command cancelled") # implement a cancel command
    return ConversationHandler.END

def get_add_sticker_conv():
    return ConversationHandler(
        entry_points=[CommandHandler("addsticker", new_sticker)],
        states={
            SELECTING_PACK: [MessageHandler(filters.ALL, select_pack)],
            SELECTING_STICKER: [MessageHandler(filters.ALL, select_sticker)],
            SELECTING_DURATION: [MessageHandler(filters.TEXT, select_duration)],
            SELECTING_EMOJI: [MessageHandler(filters.TEXT, select_emoji)]
            },
        fallbacks=[MessageHandler(filters.ALL, cancel)]
    )
