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


@pytest.mark.parametrize(
    "position, index",
    [
        ((0, 0), (0, 0)),
        ((10, 30), (0, 0)),
        ((-10, -30), (-1, -1)),
        ((250, 250), (2, 1)),
    ]
)
def test_tile_index(world, position, index):
    assert world.index(position) == index


@pytest.mark.parametrize(
    "position, tile_coordinates",
    [
        ((0, 0), (0, 0)),
        ((10, 30), (10, 30)),
        ((-10, -30), (90, 170)),
        ((250, 250), (50, 50)),
    ]
)
def test_tile_coordinate(world, position, tile_coordinates):
    assert world.tile_coordinate(position) == tile_coordinates
