import pygame  # pyright: ignore[reportMissingImports]
from typing import Optional, Tuple, List
import sys


class Player:
    def __init__(
        self, x: int, y: int, build: bool, size: Optional[int] = None
    ) -> None:
        self.build: bool = build
        base_path = "_internal/assets" if self.build else "src/entities/assets"
        try:
            self.sprites: List[pygame.Surface] = [
                pygame.image.load(f"{base_path}/pacman_1.png"),
                pygame.image.load(f"{base_path}/pacman_2.png"),
                pygame.image.load(f"{base_path}/pacman_3.png"),
                pygame.image.load(f"{base_path}/pacman_2.png"),
            ]
        except Exception:
            print("Sprite not found", file=sys.stderr)
            sys.exit(1)
        self.size: Optional[Tuple[int, int]] = None
        if size:
            self.size = (size, size)
            self.sprites = [
                pygame.transform.smoothscale(img, self.size)
                for img in self.sprites
            ]
        self.current_frame: int = 0
        self.animation_fps: int = 10
        self.animation_timer: float = 0.0
        self._last_ticks: Optional[int] = None
        self.direction: int = 2
        self.dying: bool = False
        self.image: pygame.Surface = self._apply_direction(self.sprites[0])
        self.rect: pygame.Rect = self.image.get_rect(x=x, y=y)

    def _apply_direction(self, image: pygame.Surface) -> pygame.Surface:
        center = self.rect.center if hasattr(self, "rect") else None
        if self.direction == 1:
            image = pygame.transform.rotate(image, 90)
        elif self.direction == 4:
            image = pygame.transform.rotate(image, -90)
        elif self.direction == 8:
            image = pygame.transform.flip(image, True, False)

        if center is None:
            return image

        rect = image.get_rect(center=center)
        self.rect = rect
        return image

    def set_direction(self, direction: int) -> None:
        self.direction = direction
        self.image = self._apply_direction(self.sprites[self.current_frame])

    def death(self) -> None:
        self.dying = True
        base_path = "_internal/assets" if self.build else "src/entities/assets"
        try:
            self.dying_sprites: List[pygame.Surface] = [
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
        except Exception:
            print("Sprite not found", file=sys.stderr)
            sys.exit(1)
        if self.size:
            self.dying_sprites = [
                (
                    pygame.transform.smoothscale(img, self.size)
                    if img is not None
                    else None
                )
                for img in self.dying_sprites
            ]
        self.image = self.dying_sprites[0]

    def update(self, dt: Optional[float] = None) -> None:
        if dt is None:
            now = pygame.time.get_ticks()
            if self._last_ticks is None:
                self._last_ticks = now
                return
            dt = (now - self._last_ticks) / 1000.0
            self._last_ticks = now
        else:
            dt = float(dt)
            self.animation_timer += dt

        interval = 1.0 / max(1, self.animation_fps)

        if self.dying and self.current_frame >= len(self.dying_sprites) - 1:
            if self.size is None:
                return
            transparent = pygame.Surface(self.size, pygame.SRCALPHA)
            transparent.fill((0, 0, 0, 0))
            self.image = transparent
            return

        if self.animation_timer >= interval and self.dying:
            steps = int(self.animation_timer // interval)
            self.animation_timer -= steps * interval
            self.current_frame = self.current_frame + steps
            self.image = self.dying_sprites[self.current_frame]
        elif self.animation_timer >= interval:
            steps = int(self.animation_timer // interval)
            self.animation_timer -= steps * interval
            self.current_frame = ((self.current_frame + steps)
                                  % len(self.sprites))
            self.image = self._apply_direction(
                self.sprites[self.current_frame])

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
