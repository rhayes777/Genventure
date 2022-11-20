import logging
import os
import shutil
from functools import cached_property
from os import environ
from pathlib import Path

import cv2
import openai
import requests
from PIL import Image as PILImage

IMAGE_DIRECTORY = Path(environ["IMAGE_DIRECTORY"])
os.makedirs(IMAGE_DIRECTORY, exist_ok=True)

openai.api_key = environ["API_KEY"]


class Image:
    def __init__(self, prompt, width=1024, height=1024, ):
        self.prompt = prompt
        self.width = width
        self.height = height
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


class SpriteImage(Image):
    def download(self):
        super().download()

        self.logger.info("Removing background...")
        filename = str(self.path)

        src = cv2.imread(filename, 1)
        tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
        b, g, r = cv2.split(src)
        rgba = [b, g, r, alpha]
        dst = cv2.merge(rgba, 4)
        cv2.imwrite(filename, dst)
