import asyncio
from io import BytesIO

import PIL.Image as Image

from conversation.utils import async_request


def process_image(image_url: str):
    async def process():
        image = Image.open(await async_request(image_url))
        width, height = image.size
        scale = 512 / max(width, height)
        new_width, new_height = int(width * scale), int(height * scale)
        image = image.resize((new_width, new_height))
        image = image.convert("RGBA")
        out = BytesIO()
        image.save(out, format="png")
        return out.getvalue()

    return asyncio.create_task(process())
