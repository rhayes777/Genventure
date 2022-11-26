import logging
from threading import Thread

import pygame
from pygame.locals import *

from genventure.image import make_player_image

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

pygame.init()
info = pygame.display.Info()

width = info.current_w
height = info.current_h


class Player(pygame.sprite.Sprite):
    def __init__(self, player_prompt, world):
        super().__init__()
        image_thread = Thread(target=self.load_player_image, args=(player_prompt,))
        image_thread.start()

        self.is_left = True

        self.position = [320, 200]

        self.world = world

        self.player_image = None
        self.left_image = None
        self.right_image = None

    def load_player_image(self, player_prompt):
        self.player_image = make_player_image(player_prompt)
        if not self.player_image.exists():
            self.player_image.download()

        image_path = str(self.player_image.path)

        self.left_image = pygame.image.load(image_path)
        self.right_image = pygame.transform.flip(self.left_image.copy(), True, False, )

        self.rect = self.image.get_rect()

    @property
    def tile(self):
        return self.world.tile_for_position(self.position)

    @property
    def image(self):
        return self.left_image if self.is_left else self.right_image

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_UP] or pressed_keys[K_w]:
            self.position[1] -= 5
        if pressed_keys[K_DOWN] or pressed_keys[K_s]:
            self.position[1] += 5
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            self.position[0] -= 5
            self.is_left = True
        if pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            self.position[0] += 5
            self.is_left = False

    def draw(self, surface):
        if self.image is None:
            return 

        self.rect.center = self.world.tile_coordinate(self.position)
        surface.blit(self.image, self.rect)


class Game:
    def __init__(self, player_prompt, world):
        self._running = True
        self._surface = None

        self.clock = pygame.time.Clock()
        self.player = None

        self.player = Player(
            player_prompt,
            world=world
        )

        self.world = world

    def on_init(self):
        self._surface = pygame.display.set_mode(self.world.tile_shape, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.player.update()

    def on_render(self):
        tile = self.player.tile
        if tile is not None:
            background = pygame.image.load(
                self.player.tile.image.path
            )
            self._surface.blit(background, (0, 0))
        else:
            self._surface.fill((255, 255, 255))

        for flora in tile.flora:
            flora.draw(self._surface)

        self.player.draw(self._surface)
        pygame.display.update()

    def on_cleanup(self):
        self.player = None
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.clock.tick(60)

        self.on_cleanup()
