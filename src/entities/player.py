import pygame


class Player:
    def __init__(s, x, y):
        s.sprites = [
            pygame.image.load("src/entities/assets/pacman_1.png"),
            pygame.image.load("src/entities/assets/pacman_2.png"),
            # pygame.image.load("src/entities/assets/pacman_3.png"),
            pygame.image.load("src/entities/assets/pacman_4.png"),
            # pygame.image.load("src/entities/assets/pacman_3.png"),  # ca accelere l'animation je prefere comme ca, go demander a gaspare ce qu'il en pense
            pygame.image.load("src/entities/assets/pacman_2.png")
        ]
        s.current_frame = 0
        s.frame_count = 0
        s.animation_speed = 10

        s.image = s.sprites[0]
        s.rect = s.image.get_rect(x=x, y=y)

    def update(s):
        s.frame_count += 1

        if s.frame_count >= s.animation_speed:
            s.frame_count = 0
            s.current_frame = (s.current_frame + 1) % len(s.sprites)
            s.image = s.sprites[s.current_frame]

    def draw(self, screen):
        screen.blit(self.image, self.rect)
