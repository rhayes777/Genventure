from collections import Counter
from functools import cached_property

BUCKET_SIZE = 5


class BackgroundRemover:
    def __init__(self, image):
        self.image = image

    @cached_property
    def background_bucket(self):
        color_buckets = Counter()

        for edge in (
                self.image[0, :],
                self.image[:, 0],
                self.image[self.image.shape[0] - 1, :],
                self.image[:, self.image.shape[1] - 1],
        ):
            for color in edge:
                bucket_value = tuple(
                    channel % BUCKET_SIZE
                    for channel in color
                )
                color_buckets[bucket_value] += 1

        return max(color_buckets, key=lambda bucket: color_buckets[bucket])
