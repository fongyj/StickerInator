# help
HELP_MESSAGE = (
    "StickerInator is made to help you with creating stickerpacks with images, videos and telegram bubbles!\n\n"
    + "Available commands:\n"
    + "/newpack - Creates a new stickerpack\n"
    + "/addsticker - Adds a sticker\n"
    + "/delsticker - Deletes a sticker\n"
    + "/delpack - Deletes a stickerpack"
)

# add pack/sticker
PACK_NAME_MESSAGE = "Please reply with sticker pack name"

PACK_TITLE_MESSAGE = "Please reply with sticker pack title"

PACK_TYPE_MESSAGE = "Please reply with sticker pack type: IMAGE or VIDEO"

WRONG_PACK_TYPE_MESSAGE = "Please reply with IMAGE or VIDEO"

IMAGE_STICKER_MESSAGE = "Please send image sticker"

VIDEO_STICKER_MESSAGE = "Please send video sticker"

VIDEO_CROP_MESSAGE = (
    "Video duration is {} seconds, maximum duration is 3 seconds\n"
    + 'Crop video by replying with start time followed by duration "mm:ss.S s.S"\n'
    + "(m for minutes, s for seconds, S for fraction of a second)\n\n"
    + 'Reply with "OK" if no video cropping is needed'
)

INVALID_VIDEO_DURATION_MESSAGE = (
    'Invalid start timestamp and duration, reply with start time followed by duration"mm:ss.S s.S"\n'
    + "(m for minutes, s for seconds, S for fraction of a second)"
)

STICKER_EMOJI_MESSAGE = "Please send a emoji for the sticker"

ADD_NEXT_STICKER_MESSAGE = (
    "Please send another sticker OR reply with DONE when finished"
)

STICKER_FROM_SET_MESSAGE = "Please send a sticker from your sticker set"

ADD_SUCCESS_MESSAGE = "Added stickers!"

NEXT_STICKER_MESSAGE = "Please send another sticker OR reply with DONE when finished"

VIDEO_TOO_LONG_MESSAGE = (
    'Video duration is too long, crop video by replying with start time followed by duration"mm:ss.S s.S"\n'
    + "(m for minutes, s for seconds, S for fraction of a second)"
)

CREATE_PACK_SUCCESS_MESSAGE = "Sticker pack created: https://t.me/addstickers/{}"

# delete pack
DELETE_PACK_CONFIRMATION_MESSAGE = "Confirm delete pack? Reply with YES"

DELETE_PACK_SUCCESS_MESSAGE = "Sticker pack {} deleted"

SET_NOT_FOUND_MESSAGE = "No such sticker/stickerset. Cancelling operation"

# delete sticker
DELETE_STICKER_MESSAGE = "Please send the sticker you wish to delete"

LAST_STICKER_MESSAGE = "This is your last sticker. Deleting this will delete the sticker pack. Are you sure? Reply with YES"

DELETE_STICKER_CONFIRMATION_MESSAGE = "Confirm delete sticker? Reply with YES"

STICKER_NOT_FOUND_MESSAGE = "Sticker not found in the sticker set."

DELETE_STICKER_SUCCESS_MESSAGE = "Sticker deleted from {}"
