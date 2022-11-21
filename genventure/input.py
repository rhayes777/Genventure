import pygame
import pygame_textinput

pygame.init()


def text_input(callback):
    # Create TextInput-object
    textinput = pygame_textinput.TextInputVisualizer()

    screen = pygame.display.set_mode((1000, 200))
    clock = pygame.time.Clock()

    loop = True

    while loop:
        screen.fill((225, 225, 225))

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                loop = False
                callback(textinput.value)

        # Feed it with events every frame
        textinput.update(events)
        # Blit its surface onto the screen
        screen.blit(textinput.surface, (10, 10))

        for event in events:
            if event.type == pygame.QUIT:
                exit()

        pygame.display.update()
        clock.tick(30)
