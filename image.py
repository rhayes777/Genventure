import logging
import os
import shutil
import uuid
from abc import abstractmethod, ABC
from functools import cached_property
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


class AbstractImage(ABC):
    def __init__(self, width=1024, height=1024, transparent_background=False, ):
        self.width = width
        self.height = height
        self.transparent_background = transparent_background

        self.logger = logging.getLogger(self.name)

    @property
    @abstractmethod
    def name(self):
        pass

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
    @abstractmethod
    def url(self):
        pass

    def exists(self):
        return self.path.exists()

    @property
    def path(self):
        return (IMAGE_DIRECTORY / self.name).with_suffix(".png")

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


class Image(AbstractImage):
    def __init__(self, prompt, width=1024, height=1024, transparent_background=False, ):
        self.prompt = prompt
        super().__init__(
            width=width,
            height=height,
            transparent_background=transparent_background,
        )

    @property
    def name(self):
        return self.prompt

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
    def url(self):
        return self.query_response['data'][0]['url']

    def variations(self, n: int = 1) -> List["Variation"]:
        return [Variation(self) for _ in range(n)]
        # with open(self.path, "rb") as f:
        #     response = openai.Image.create_variation(
        #         image=f,
        #         n=n,
        #         size=self.requested_size,
        #     )
        # return [
        #     URLImage(
        #         name=f"{self.name}_{str(uuid.uuid4())[:8]}",
        #         url=response_dict['url'],
        #         width=self.width,
        #         height=self.height,
        #         transparent_background=self.transparent_background,
        #     )
        #     for response_dict in response['data']
        # ]


class Variation(Image):
    def __init__(self, image):
        self.image = image
        super().__init__(
            prompt=image.prompt,
            width=image.width,
            height=image.height,
            transparent_background=image.transparent_background,
        )

    @cached_property
    def name(self):
        return f"{self.image.name}_{str(uuid.uuid4())[:8]}"


class URLImage(AbstractImage):
    def __init__(self, name, url, width=1024, height=1024, transparent_background=False, ):
        super().__init__(
            width=width,
            height=height,
            transparent_background=transparent_background,
        )
        self._url = url
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url


# response = openai.Image.create_variation(
#     image=open("corgi_and_cat_paw.png", "rb"),
#     n=1,
#     size="1024x1024"
# )
# image_url = response['data'][0]['url']


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
            f"beautiful top down view video game art of {noun}",
            width=width,
            height=height,
            transparent_background=transparent_background,
        )


if __name__ == "__main__":
    image = BackgroundImage("volcano", 1024, 1024)
    variation, = image.variations()
    variation.download()
