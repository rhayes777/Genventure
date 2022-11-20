import logging
import os
import shutil
from functools import cached_property
from os import environ
from pathlib import Path
from PIL import Image as PILImage

import cv2
import numpy as np
import openai
import requests

IMAGE_DIRECTORY = Path(environ["IMAGE_DIRECTORY"])
os.makedirs(IMAGE_DIRECTORY, exist_ok=True)

openai.api_key = environ["API_KEY"]


class Image:
    def __init__(self, prompt, width=1024, height=1024, transparent_background=False, ):
        self.prompt = prompt
        self.width = width
        self.height = height
        self.transparent_background = transparent_background
        self.logger = logging.getLogger(prompt)

    @cached_property
    def query_response(self):
        self.logger.info("Querying API...")
        response = openai.Image.create(
            prompt=self.prompt,
            n=1,
            size=self.requested_size,
        )
        self.logger.info("Query complete")
        return response

    @property
    def requested_size(self):
        biggest = max(self.width, self.height)
        if biggest > 512:
            return '1024x1024'
        if biggest > 256:
            return '512x512'
        return '256x256'

    @property
    def shape(self):
        return self.width, self.height

    @property
    def url(self):
        return self.query_response['data'][0]['url']

    def exists(self):
        return self.path.exists()

    @property
    def path(self):
        return (IMAGE_DIRECTORY / self.prompt).with_suffix(".png")

    def download(self):
        url = self.url
        self.logger.info("Downloading...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(self.path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        self.logger.info("Download complete. Resizing...")

        image = PILImage.open(self.path)

        sunset_resized = image.resize(self.shape)
        sunset_resized.save(self.path)

        if self.transparent_background:
            self.logger.info("Removing background...")
            filename = str(self.path)

            src = cv2.imread(filename, 1)

            grey = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

            ret, baseline = cv2.threshold(grey, 127, 255, cv2.THRESH_TRUNC)

            ret, background = cv2.threshold(baseline, 126, 255, cv2.THRESH_BINARY)

            alpha = np.full(src.shape[:2], 255, dtype=np.uint8)
            alpha[background == 255] = 0

            b, g, r = cv2.split(src)
            rgba = [b, g, r, alpha]
            dst = cv2.merge(rgba, 4)
            cv2.imwrite(filename, dst)


def bgremove2(myimage):
    # First Convert to Grayscale
    myimage_grey = cv2.cvtColor(myimage, cv2.COLOR_BGR2GRAY)

    ret, baseline = cv2.threshold(myimage_grey, 127, 255, cv2.THRESH_TRUNC)

    ret, background = cv2.threshold(baseline, 126, 255, cv2.THRESH_BINARY)

    ret, foreground = cv2.threshold(baseline, 126, 255, cv2.THRESH_BINARY_INV)

    foreground = cv2.bitwise_and(myimage, myimage,
                                 mask=foreground)  # Update foreground with bitwise_and to extract real foreground

    # Convert black and white back into 3 channel greyscale
    background = cv2.cvtColor(background, cv2.COLOR_GRAY2BGR)

    # Combine the background and foreground to obtain our final image
    finalimage = background + foreground
    return finalimage


class PlayerImage(Image):
    def __init__(self, noun, width=32, height=32, transparent_background=True, ):
        super().__init__(
            f"Pixel art of a {noun} facing right",
            width=width,
            height=height,
            transparent_background=transparent_background,
        )


class BackgroundImage(Image):
    def __init__(self, noun, width, height, transparent_background=False, ):
        super().__init__(
            f"Isometric video game background of {noun}",
            width=width,
            height=height,
            transparent_background=transparent_background,
        )
