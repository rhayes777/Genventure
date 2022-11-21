from time import sleep

import pytest

from genventure.world import World


class MockImage:
    def variations(self, n=1):
        return [
            MockImage()
            for _ in range(n)
        ]

    def download(self):
        pass


@pytest.fixture(
    name="image"
)
def make_image():
    return MockImage()


@pytest.fixture(
    name="world"
)
def make_world(image):
    return World(image, tile_shape=(100, 200))


def test_get_tile(image, world):
    tile = world[0, 0]
    assert tile.image == image


def test_neighbors(image, world):
    _ = world[0, 0]
    sleep(0.1)

    tile = world[1, 1]
    assert tile.image != image
    assert tile.image == world[1, 1].image
    assert tile.image != world[-1, -1].image