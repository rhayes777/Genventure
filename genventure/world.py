import math
import uuid
from queue import Queue
from threading import Thread

from genventure.image import make_background_images


class Tile:
    def __init__(self, image):
        self.image = image


class World:
    def __init__(self, background_prompt, tile_shape):
        self.background_prompt = background_prompt
        self.tile_shape = tile_shape

        self._tile_cache = {}
        self.image_queue = Queue()
        background_thread = Thread(target=self.add_to_queue, args=(3,))
        background_thread.start()

    def add_to_queue(self, n=1):
        images = make_background_images(
            noun=self.background_prompt,
            width=self.tile_shape[0],
            height=self.tile_shape[1],
            n=n
        )
        for image in images:
            image.name = f"{self.background_prompt}_{uuid.uuid4()}"
            image.download()
            self.image_queue.put(image)

    def __getitem__(self, item):
        if item not in self._tile_cache:
            background_thread = Thread(target=self.add_to_queue)
            background_thread.start()
            self._tile_cache[item] = Tile(self.image_queue.get())
        return self._tile_cache[item]

    def index(self, position):
        return math.floor(position[0] / self.tile_shape[0]), math.floor(position[1] / self.tile_shape[1])

    def tile_coordinate(self, position):
        return position[0] % self.tile_shape[0], position[1] % self.tile_shape[1]

    def tile_for_position(self, position):
        return self[self.index(position)]
