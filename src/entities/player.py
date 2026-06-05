import pygame


class Player:
    def __init__(s, x, y, build, size=None):
        s.build = build
        base_path = "_internal/assets" if s.build else "src/entities/assets"
        s.sprites = [
            pygame.image.load(f"{base_path}/pacman_1.png"),
            pygame.image.load(f"{base_path}/pacman_2.png"),
            pygame.image.load(f"{base_path}/pacman_3.png"),
            pygame.image.load(f"{base_path}/pacman_2.png")
        ]
        if size:
            s.size = (size, size)
            s.sprites = [pygame.transform.smoothscale(
                img, s.size) for img in s.sprites]
        s.current_frame = 0
        s.animation_fps = 10
        s.animation_timer = 0.0
        s._last_ticks = None
        s.direction = 2
        s.dying = False
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

    def death(s):
        s.dying = True
        base_path = "_internal/assets" if s.build else "src/entities/assets"
        s.dying_sprites = [
            pygame.image.load(f"{base_path}/dying/dying_1.png"),
            pygame.image.load(f"{base_path}/dying/dying_2.png"),
            pygame.image.load(f"{base_path}/dying/dying_3.png"),
            pygame.image.load(f"{base_path}/dying/dying_4.png"),
            pygame.image.load(f"{base_path}/dying/dying_5.png"),
            pygame.image.load(f"{base_path}/dying/dying_6.png"),
            pygame.image.load(f"{base_path}/dying/dying_7.png"),
            pygame.image.load(f"{base_path}/dying/dying_8.png"),
            pygame.image.load(f"{base_path}/dying/dying_9.png"),
            pygame.image.load(f"{base_path}/dying/dying_10.png"),
            pygame.image.load(f"{base_path}/dying/dying_11.png"),
        ]
        if s.size:
            s.dying_sprites = [
                (pygame.transform.smoothscale(img, s.size)
                 if img is not None else None)
                for img in s.dying_sprites
            ]
        s.image = s.dying_sprites[0]

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

        if s.dying and s.current_frame >= len(s.dying_sprites) - 1:
            transparent = pygame.Surface(s.size, pygame.SRCALPHA)
            transparent.fill((0, 0, 0, 0))
            s.image = transparent
            return

        if s.animation_timer >= interval and s.dying:
            steps = int(s.animation_timer // interval)
            s.animation_timer -= steps * interval
            s.current_frame = (s.current_frame + steps)
            s.image = s.dying_sprites[s.current_frame]
        elif s.animation_timer >= interval:
            steps = int(s.animation_timer // interval)
            s.animation_timer -= steps * interval
            s.current_frame = (s.current_frame + steps) % len(s.sprites)
            s.image = s._apply_direction(s.sprites[s.current_frame])

    def draw(self, screen):
        screen.blit(self.image, self.rect)
