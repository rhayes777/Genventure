import logging
import os
import shutil
import uuid
from os import environ
from pathlib import Path
from typing import List

import cv2
import numpy as np
import openai
import requests
from PIL import Image as PILImage

IMAGE_DIRECTORY = Path(environ["IMAGE_DIRECTORY"])
os.makedirs(IMAGE_DIRECTORY, exist_ok=True)

openai.api_key = environ["API_KEY"]


class ImageShape:
    def __init__(self, width=1024, height=1024):
        self.width = width
        self.height = height

    @property
    def shape(self):
        return self.width, self.height

    def __iter__(self):
        return iter((self.width, self.height))

    @property
    def requested_size(self):
        biggest = max(self.width, self.height)
        if biggest > 512:
            return '1024x1024'
        if biggest > 256:
            return '512x512'
        return '256x256'


class LocalImage:
    def __init__(self, name):
        self.name = name

    @property
    def path(self):
        return (IMAGE_DIRECTORY / self.name).with_suffix(".png")

    @property
    def logger(self):
        return logging.getLogger(self.name)

    def exists(self):
        return self.path.exists()

    def __del__(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


class Image(LocalImage):
    def __init__(self, name, url, shape, transparent_background=False, ):
        super().__init__(name)
        self.shape = shape
        self.url = url
        self.name = name
        self.transparent_background = transparent_background

    # noinspection PyUnresolvedReferences
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

            ret, baseline = cv2.threshold(grey, 201, 255, cv2.THRESH_TRUNC)

            ret, background = cv2.threshold(baseline, 200, 255, cv2.THRESH_BINARY)

            alpha = np.full(src.shape[:2], 255, dtype=np.uint8)
            alpha[background == 255] = 0

            b, g, r = cv2.split(src)
            rgba = [b, g, r, alpha]
            dst = cv2.merge(rgba, 4)
            cv2.imwrite(filename, dst)

    @classmethod
    def for_prompt(cls, prompt, shape=None, n=1, transparent_background=False, name=None):
        shape = shape or ImageShape(width=1024, height=1024)
        logger = logging.getLogger(prompt)
        logger.info("Querying API...")
        response = openai.Image.create(
            prompt=prompt,
            n=n,
            size=shape.requested_size,
        )
        logger.info("Query complete")
        return [
            Image(
                name=name or prompt,
                url=data["url"],
                shape=shape,
                transparent_background=transparent_background
            )
            for data in response["data"]
        ]

    def variations(self, n: int = 1) -> List["Image"]:
        with open(self.path, "rb") as f:
            response = openai.Image.create_variation(
                image=f,
                n=n,
                size=self.shape.requested_size,
            )
        return [
            Image(
                name=f"{self.name}_{str(uuid.uuid4())[:8]}",
                url=response_dict['url'],
                shape=self.shape,
                transparent_background=self.transparent_background,
            )
            for response_dict in response['data']
        ]


def make_player_image(noun):
    return Image.for_prompt(prompt=f"Pixel art of a {noun} facing right",
                            shape=ImageShape(64, 64), transparent_background=True)[0]


def background_prompt(noun):
    return f"beautiful top down view video game art of {noun}"


def make_background_images(noun, width, height, n=1, name=None):
    return Image.for_prompt(
        prompt=background_prompt(noun),
        shape=ImageShape(width, height),
        transparent_background=False,
        n=n,
        name=name,
    )
