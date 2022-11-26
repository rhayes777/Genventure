import numpy as np

from genventure.background_remover import BackgroundRemover

FG = (255, 255, 255)
BG = (0, 0, 0)


def test_background_bucket():
    image = np.array([
        [BG, BG, BG, ],
        [BG, FG, BG, ],
        [BG, BG, BG, ],
    ])

    assert BackgroundRemover(image).background_bucket == BG
