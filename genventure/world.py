from threading import Thread


class Tile:
    def __init__(self, image):
        self.image = image


class World:
    def __init__(self, seed_image, tile_shape):
        self.seed_image = seed_image
        self.tile_shape = tile_shape

        self._tile_cache = {
            (0, 0): Tile(image=seed_image)
        }

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
        tile = self._tile_cache[item]
        variations = tile.image.variations(n=len(missing_coordinates))
        for coordinate_pair, image in zip(missing_coordinates, variations):
            image.download()
            self._tile_cache[coordinate_pair] = Tile(image)

    def __getitem__(self, item):
        background_thread = Thread(target=self.add_missing_tiles, args=(item,))
        background_thread.start()
        return self._tile_cache[item]
