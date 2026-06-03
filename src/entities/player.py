import pygame


class Player:
    def __init__(s, x, y, size=None):
        s.sprites = [
            pygame.image.load("src/entities/assets/pacman_1.png"),
            pygame.image.load("src/entities/assets/pacman_2.png"),
            # pygame.image.load("src/entities/assets/pacman_3.png"),
            pygame.image.load("src/entities/assets/pacman_4.png"),
            # pygame.image.load("src/entities/assets/pacman_3.png"),
            # ca accelere l'animation je prefere comme ca, go demander a
            # gaspard ce qu'il en pense
            pygame.image.load("src/entities/assets/pacman_2.png")
        ]
        if size:
            size = (size, size)
            s.sprites = [pygame.transform.smoothscale(
                img, size) for img in s.sprites]
        s.current_frame = 0
        s.animation_fps = 10
        s.animation_timer = 0.0
        s._last_ticks = None
        s.direction = 2

        s.image = s._apply_direction(s.sprites[0])
        s.rect = s.image.get_rect(x=x, y=y)

    def _apply_direction(s, image):
        center = s.rect.center if hasattr(s, "rect") else None
        if s.direction == 1:
            image = pygame.transform.rotate(image, 90)
        elif s.direction == 4:
            image = pygame.transform.rotate(image, -90)
        elif s.direction == 8:
            image = pygame.transform.flip(image, True, False)

        if center is None:
            return image

        rect = image.get_rect(center=center)
        s.rect = rect
        return image

    def set_direction(s, direction):
        s.direction = direction
        s.image = s._apply_direction(s.sprites[s.current_frame])

    def update(s, dt=None):
        if dt is None:
            now = pygame.time.get_ticks()
            if s._last_ticks is None:
                s._last_ticks = now
                return
            dt = (now - s._last_ticks) / 1000.0
            s._last_ticks = now
        else:
            dt = float(dt)

        s.animation_timer += dt
        interval = 1.0 / max(1, s.animation_fps)
        if s.animation_timer >= interval:
            steps = int(s.animation_timer // interval)
            s.animation_timer -= steps * interval
            s.current_frame = (s.current_frame + steps) % len(s.sprites)
            s.image = s._apply_direction(s.sprites[s.current_frame])

    def draw(self, screen):
        screen.blit(self.image, self.rect)
