# help
NEW_PACK_HELP = "Creates a new stickerpack"
ADD_STICKER_HELP = "Adds a sticker"
DEL_STICKER_HELP = "Deletes a sticker"
DEL_PACK_HELP = "Deletes a stickerpack"
HELP_HELP = "Gets info on the bot"
CANCEL_HELP = "Cancels current operation"
RESET_HELP = "Resets StickerInator"

HELP_MESSAGE = (
        "*StickerInator* is designed to help you create sticker packs with images, videos and telegram bubbles\!\n\n"
        + "Available commands:\n"
        + f"/newpack \- {NEW_PACK_HELP}\n"
        + f"/addsticker \- {ADD_STICKER_HELP}\n"
        + f"/delsticker \- {DEL_STICKER_HELP}\n"
        + f"/delpack \- {DEL_PACK_HELP}\n"
        + f"/help \- {HELP_HELP}\n"
        + f"/cancel \- {CANCEL_HELP}\n"
        + f"/reset \- {RESET_HELP}"
)

# add pack/sticker
PACK_TYPE_MESSAGE = "Please select a sticker type"

IMAGE_STICKER_MESSAGE = "Please send image sticker\n\nStickerInator can accept images of most file formats and existing image stickers"

VIDEO_STICKER_MESSAGE = "Please send video sticker\n\nStickerInator can accept videos of most file formats, existing video stickers and telegram video notes"

VIDEO_CROP_NOT_NECESSARY_MESSAGE = (
    "Video duration: <b>{} seconds</b>\nMaximum duration: <b>3 seconds</b>\n\n"
    "If no video cropping is needed, select <em>NO CROP</em>"
)

VIDEO_CROP_NECESSARY_MESSAGE = (
    "Video duration: <b>{} seconds</b>\nMaximum duration: <b>3 seconds</b>\n\n"
    "Video exceeds maximum allowed duration, video cropping is required"
)

VIDEO_CROP_INFO_MESSAGE = (
    "To crop the video, reply with the start time and duration in the format: "
    "<b>mm:ss.S s.S</b>\n"
    "(m for minutes, s for seconds, S for fraction of a second)\n\n"
    "For example, to crop the video starting at 5 minutes and 10.5 seconds, with a duration of 2.8 seconds, "
    "reply with: <b>05:10.5 2.8</b>"
)

INVALID_VIDEO_DURATION_MESSAGE = "Invalid start timestamp or duration"

STICKER_EMOJI_MESSAGE = "Please send a single emoji for the sticker"

NEXT_STICKER_MESSAGE = (
    "Please send another sticker or select <em>DONE</em> to create sticker pack"
)

STICKER_FROM_PACK_MESSAGE = "Please send a sticker from the existing sticker pack"

INVALID_PACK_MESSAGE = "Sticker pack selected must be created by StickerInatorBot"

ADD_SUCCESS_MESSAGE = "Added {} sticker(s)"

VIDEO_TOO_LONG_MESSAGE = "Video duration is too long"

PACK_LIMIT_REACHED_MESSAGE = (
    "Sticker pack limit reached, you cannot add more stickers\nMaximum {} stickers allowed is {}"
)

EMPTY_PACK_MESSAGE = "There is currently 0 sticker added. Please add a sticker before creating a sticker pack"

SIZE_LIMIT_REACHED_MESSAGE = (
    "Sticker file size limit reached, please send a smaller sticker"
)

PACK_TITLE_MESSAGE = "Please reply with sticker pack title"

PACK_NAME_MESSAGE = (
        "Please reply with sticker pack name"
        + "\n"
        + "Note: Sticker pack names must be unique"
)

CREATE_PACK_SUCCESS_MESSAGE = "Sticker pack created: https://t.me/addstickers/{}"

STICKER_NOT_SUPPORTED = "Sticker is animated and is currently not supported. Please send another video sticker"

# delete pack
DELETE_PACK_CONFIRMATION_MESSAGE = "Reply with <code>DELETE PACK</code> to confirm"

DELETE_PACK_SUCCESS_MESSAGE = "Sticker pack {} deleted"

PACK_NOT_FOUND_MESSAGE = "No such sticker/sticker pack. Cancelling operation"

# delete sticker
DELETE_STICKER_MESSAGE = "Please send the sticker you wish to delete"

LAST_STICKER_MESSAGE = "This is your last sticker!\nDeleting this sticker will delete the sticker pack\n\nReply with <code>DELETE STICKER</code> to confirm"

DELETE_STICKER_CONFIRMATION_MESSAGE = "Reply with <code>DELETE STICKER</code> to confirm"

STICKER_NOT_FOUND_MESSAGE = "Sticker not found in the sticker pack"

DELETE_STICKER_SUCCESS_MESSAGE = "Sticker deleted from {}"

# cancel
ACTIVE_COMMAND_MESSAGE = "Command \"{}\" is currently active in this chat or in another chat, please use /cancel or /reset before initiating another command"

UNHANDLED_TELEGRAM_ERROR_MESSAGE = "Telegram encountered an error, please try again or cancel the current operation with the cancel command"

UNHANDLED_STICKERINATOR_ERROR_MESSAGE = "StickerInator encountered an error, please try again or cancel the current operation with the cancel command"

CANCEL_MESSAGE = "Command \"{}\" cancelled"

RESET_MESSAGE = "StickerInator reset complete"