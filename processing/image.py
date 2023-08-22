import PIL.Image as Image
import requests
from io import BytesIO


def process_image(image_url: str):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    width, height = image.size
    scale = 512 / max(width, height)
    new_width, new_height = int(width * scale), int(height * scale)
    image = image.resize((new_width, new_height))
    image = image.convert("RGBA")
    out = BytesIO()
    image.save(out, format="png")
    return out.getvalue()
