import math
from queue import Queue
from random import randint, choice
from threading import Thread

import pygame

from genventure.image import make_background_images, make_flora_images


class Flora(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path)

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Tile:
    def __init__(self, image, flora_images, shape):
        self.image = image
        self.flora_images = flora_images
        self.shape = shape

        if len(flora_images) == 0:
            self.flora = []
        else:
            self.flora = [
                Flora(
                    image_path=choice(self.flora_images).path,
                    x=randint(0, self.shape[0]),
                    y=randint(0, self.shape[1]),
                )
                for _ in range(randint(0, 30))
            ]


class World:
    def __init__(self, noun, tile_shape):
        self.noun = noun
        self.tile_shape = tile_shape

        self._tile_cache = {}
        self.image_queue = Queue()
        self.flora_images = []

        background_thread = Thread(target=self.add_to_queue, args=(3,))
        background_thread.start()

        flora_thread = Thread(target=self.generate_flora_images)
        flora_thread.start()

    def generate_flora_images(self, n=6):
        flora_images = make_flora_images(n=n, noun=self.noun)
        for image in flora_images:
            image.download()
        self.flora_images = flora_images

    def add_to_queue(self, n=1):
        images = make_background_images(
            noun=self.noun,
            width=self.tile_shape[0],
            height=self.tile_shape[1],
            n=n
        )
        for image in images:
            image.download()
            self.image_queue.put(image)

    def __getitem__(self, item):
        if item not in self._tile_cache:
            background_thread = Thread(target=self.add_to_queue)
            background_thread.start()
            self._tile_cache[item] = Tile(
                self.image_queue.get(),
                flora_images=self.flora_images,
                shape=self.tile_shape,
            )
        return self._tile_cache[item]

    def index(self, position):
        return math.floor(position[0] / self.tile_shape[0]), math.floor(position[1] / self.tile_shape[1])

    def tile_coordinate(self, position):
        return position[0] % self.tile_shape[0], position[1] % self.tile_shape[1]

    def tile_for_position(self, position):
        return self[self.index(position)]
