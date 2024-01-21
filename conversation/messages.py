# help
NEW_PACK_HELP = "Creates a new stickerpack"
ADD_STICKER_HELP = "Adds a sticker"
DEL_STICKER_HELP = "Deletes a sticker"
DEL_PACK_HELP = "Deletes a stickerpack"
HELP_HELP = "Gets info on the bot"
CANCEL_HELP = "Cancels current operation"

HELP_MESSAGE = (
    "*StickerInator* is made to help you with creating stickerpacks with images, videos and telegram bubbles\!\n\n"
    + "Available commands:\n"
    + f"/newpack \- {NEW_PACK_HELP}\n"
    + f"/addsticker \- {ADD_STICKER_HELP}\n"
    + f"/delsticker \- {DEL_STICKER_HELP}\n"
    + f"/delpack \- {DEL_PACK_HELP}\n"
    + f"/help \- {HELP_HELP}\n"
    + f"/cancel \- {CANCEL_HELP}\n\n"
    + "Find the source code for StickerInator [here](https://github.com/fongyj/StickerInator)"
)

# add pack/sticker
PACK_TYPE_MESSAGE = "Please select a sticker type:"

IMAGE_STICKER_MESSAGE = "Please send image sticker\n\nStickerInator can accept images of most file formats and existing image stickers"

VIDEO_STICKER_MESSAGE = "Please send video sticker\n\nStickerInator can accept videos of most file formats, existing video stickers and telegram video notes"

VIDEO_CROP_NOT_NECESSARY_MESSAGE = (
    "Video duration: <b>{} seconds</b>\nMaximum duration: <b>3 seconds</b>\n\n"
    "If no video cropping is needed, select <em>No Crop</em>"
)

VIDEO_CROP_NECESSARY_MESSAGE = (
    "Video duration: <b>{} seconds</b>\nMaximum duration: <b>3 seconds</b>\n\n"
    "Video exceeds maximum allowed duration, video cropping is required"
)

VIDEO_CROP_INFO_MESSAGE = (
    "To crop the video, reply with the start time and duration in the format: "
    "<b>mm:ss.S s.S</b>\n"
    "(m for minutes, s for seconds, S for fraction of a second)\n\n"
    "For example, to crop the video starting at 5 minutes and 10.5 seconds, for a duration of 2.8 seconds, "
    "reply with: <b>05:10.5 2.8</b>"
)

INVALID_VIDEO_DURATION_MESSAGE = "Invalid start timestamp or duration"

STICKER_EMOJI_MESSAGE = "Please send a single emoji for the sticker"

NEXT_STICKER_MESSAGE = (
    "Please send another sticker or select DONE to create sticker pack"
)

STICKER_FROM_SET_MESSAGE = "Please send a sticker from your sticker set"

INVALID_SET_MESSAGE = "Sticker set selected must be created by StickerInatorBot"

ADD_SUCCESS_MESSAGE = "Added {} sticker(s)"

VIDEO_TOO_LONG_MESSAGE = "Video duration is too long"

VIDEO_PROCESSING_MESSAGE = "Please wait, video is processing... ⏰"

PACK_LIMIT_REACHED_MESSAGE = (
    "Sticker pack limit reached, you cannot add more stickers\nMaximum {} stickers allowed is {}"
)

EMPTY_PACK_MESSAGE = "There is currently 0 stickers added. Please add stickers before creating a sticker pack"

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

DOWNLOAD_FAILED_IMAGE = "Failed to download sticker. Please send another image sticker"

DOWNLOAD_FAILED_VIDEO = "Failed to download sticker. Please send another video sticker"

# delete pack
DELETE_PACK_CONFIRMATION_MESSAGE = "Reply with <b>DELETE PACK</b> to confirm"

DELETE_PACK_SUCCESS_MESSAGE = "Sticker pack {} deleted"

SET_NOT_FOUND_MESSAGE = "No such sticker/stickerset. Cancelling operation"

# delete sticker
DELETE_STICKER_MESSAGE = "Please send the sticker you wish to delete"

LAST_STICKER_MESSAGE = "❗❗❗ This is your last sticker ❗❗❗\nDeleting this sticker will delete the sticker pack\n\nReply with <b>DELETE STICKER</b> to confirm"

DELETE_STICKER_CONFIRMATION_MESSAGE = "Reply with <b>DELETE STICKER</b> to confirm"

STICKER_NOT_FOUND_MESSAGE = "Sticker not found in the sticker set"

DELETE_STICKER_SUCCESS_MESSAGE = "Sticker deleted from {}"

# cancel
CANCEL_MESSAGE = "Operation cancelled"
