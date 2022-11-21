import logging

import pygame
from pygame.locals import *

from genventure.image import PlayerImage, BackgroundImage

logging.basicConfig(level=logging.INFO)

pygame.init()


class Player(pygame.sprite.Sprite):
    def __init__(self, image_path):
        super().__init__()
        self.is_left = True

        self.left_image = pygame.image.load(image_path)
        self.right_image = pygame.transform.flip(self.left_image.copy(), True, False, )
        self.rect = self.image.get_rect()
        self.rect.center = (320, 200)

    @property
    def image(self):
        return self.left_image if self.is_left else self.right_image

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
            self.is_left = True
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)
            self.is_left = False

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Game:
    def __init__(self, player_prompt, background_prompt):
        self._running = True
        self._surface = None

        info = pygame.display.Info()

        self.width = info.current_w
        self.height = info.current_h
        self.clock = pygame.time.Clock()
        self.player = None

        self.player_image = PlayerImage(player_prompt)
        if not self.player_image.exists():
            self.player_image.download()

        self.background_image = BackgroundImage(
            noun=background_prompt,
            width=self.width,
            height=self.height,
        )
        if not self.background_image.exists():
            self.background_image.download()

        self.background = pygame.image.load(self.background_image.path)

    @property
    def shape(self):
        return self.width, self.height

    def on_init(self):
        self._surface = pygame.display.set_mode(self.shape, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
        self.player = Player(image_path=str(self.player_image.path))

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.player.update()

    def on_render(self):
        self._surface.blit(self.background, (0, 0))
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


if __name__ == "__main__":
    app = Game(
        player_prompt="queen",
        background_prompt="heaven",
    )
    app.on_execute()
