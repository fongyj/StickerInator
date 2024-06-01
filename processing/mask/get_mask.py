import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import numpy as np


def get_mask(size):
    mask = np.zeros((size, size))
    mask = Image.fromarray(mask).convert("L")
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    mask.save("mask.png")


def get_RGBA_mask(size):
    mask = np.zeros((size, size, 4))
    mask = Image.fromarray(mask, mode="RGBA")
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    mask.save("mask_RGBA.png")


if __name__ == "__main__":
    get_mask(512)
