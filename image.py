import os
import shutil
from functools import cached_property
from os import environ
from pathlib import Path

import openai
import requests

IMAGE_DIRECTORY = Path(environ["IMAGE_DIRECTORY"])
os.makedirs(IMAGE_DIRECTORY, exist_ok=True)

openai.api_key = environ["API_KEY"]


class Image:
    def __init__(self, prompt, width=1024, height=1024,):
        self.prompt = prompt
        self.width = width
        self.height = height

    @cached_property
    def query_response(self):
        return openai.Image.create(
            prompt=self.prompt,
            n=1,
            size=self.size,
        )

    @property
    def size(self):
        return f"{self.width}x{self.height}"

    @property
    def image_url(self):
        return self.query_response['data'][0]['url']

    def exists(self):
        return self.image_path.exists()

    @property
    def image_path(self):
        return (IMAGE_DIRECTORY / self.prompt).with_suffix(".png")

    def download(self):
        response = requests.get(self.image_url, stream=True)
        response.raise_for_status()
        with open(self.image_path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)


image = Image(
    prompt="Pixel art of a horse",
)
image.download()
