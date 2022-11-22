import math
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
        self.add_missing_tiles(item=(0, 0))

    def add_missing_tiles(self, item):

        coordinates = [
            (item[0] + x, item[1] + y)
            for x in range(-1, 2)
            for y in range(-1, 2)
        ]
        missing_coordinates = [
            coordinate_pair
            for coordinate_pair in coordinates
            if coordinate_pair not in self._tile_cache
        ]

        n = len(missing_coordinates)

        if n > 0:
            images = make_background_images(noun=self.background_prompt, width=self.tile_shape[0],
                                            height=self.tile_shape[1], n=n)
            for coordinate_pair, image in zip(missing_coordinates, images):
                image.name = f"{image.name}_{'_'.join(map(str, coordinate_pair))}"
                image.download()
                self._tile_cache[coordinate_pair] = Tile(image)

    def __getitem__(self, item):
        background_thread = Thread(target=self.add_missing_tiles, args=(item,))
        background_thread.start()
        return self._tile_cache[item]

    def index(self, position):
        return math.floor(position[0] / self.tile_shape[0]), math.floor(position[1] / self.tile_shape[1])

    def tile_coordinate(self, position):
        return position[0] % self.tile_shape[0], position[1] % self.tile_shape[1]

    def tile_for_position(self, position):
        return self[self.index(position)]
