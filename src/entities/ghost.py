"""Base animated ghost entity."""

import pygame
from typing import Dict, List
import sys


class Ghost:
    """Represent a ghost sprite and its visual state."""

    DIRECTIONS: Dict[int, str] = {
        1: "up",
        2: "right",
        4: "down",
        8: "left",
    }

    def __init__(
        self,
        x: int,
        y: int,
        color: str,
        size: int,
        direction: str,
        build: bool,
    ) -> None:
        """Load ghost sprites and create the collision rectangle.

        Args:
            x: Initial horizontal position in pixels.
            y: Initial vertical position in pixels.
            color: Ghost color used to select sprite assets.
            size: Square sprite size in pixels.
            direction: Initial visual direction.
            build: Whether resources are loaded from a packaged build.
        """
        self.color: str = color
        self.direction: str = direction
        self.size: int = size
        self.build: bool = build
        self.modifier: str | None = None
        self.killed: bool = False
        self.sprites: List[pygame.Surface] = self.load_sprites()
        self.current_frame: int = 0
        self.frame_count: int = 0
        self.animation_speed: int = 10

        self.image: pygame.Surface = self.sprites[0]
        self.rect: pygame.Rect = self.image.get_rect(x=x, y=y)

    def get_sprite_path(self, frame: int) -> str:
        """Build the path for one sprite frame.

        Args:
            frame: One-based animation frame number.

        Returns:
            Path to the sprite matching the ghost's current state.
        """
        base_path: str = (
            "_internal/assets" if self.build else "src/entities/assets"
        )

        try:
            if self.killed:
                return (
                    f"{base_path}/kill/{self.direction}/"
                    f"kill_{self.direction}_{frame}.png"
                )
            if self.modifier is not None:
                return (
                    f"{base_path}/modifier/{self.modifier}/"
                    f"modifier_{self.modifier}_{frame}.png"
                )

            return (
                f"{base_path}/{self.color}/{self.direction}/"
                f"{self.color}_{self.direction}_{frame}.png"
            )
        except Exception:
            print("Sprite not found", file=sys.stderr)
            sys.exit(1)

    def load_sprites(self) -> List[pygame.Surface]:
        """Load and resize the two frames for the current visual state.

        Returns:
            Loaded Pygame surfaces for the current animation.

        Raises:
            pygame.error: If a sprite file cannot be loaded.
        """
        sprites: List[pygame.Surface] = []

        for frame in range(1, 3):
            path = self.get_sprite_path(frame)
            image = pygame.image.load(path)
            sprites.append(
                pygame.transform.scale(image, (self.size, self.size)))

        return sprites

    def set_direction(self, direction: int | str) -> None:
        """Change the visual direction while preserving the sprite center.

        Args:
            direction: Direction bit or direction name.
        """
        if isinstance(direction, int):
            direction_val = self.DIRECTIONS.get(direction, None)
            direction_str = (
                direction_val if direction_val is not None else str(direction)
            )
        else:
            direction_str = str(direction)
        if direction_str == self.direction:
            return

        center = self.rect.center
        self.direction = direction_str
        self.sprites = self.load_sprites()
        self.current_frame %= 2
        self.image = self.sprites[self.current_frame]
        self.rect = self.image.get_rect(center=center)

    def set_modifier(self, modifier: str | None) -> None:
        """Apply or clear a vulnerable-state sprite modifier.

        Args:
            modifier: Modifier asset name, or ``None`` for normal sprites.
        """
        if modifier == self.modifier:
            return

        center = self.rect.center
        self.modifier = modifier
        self.sprites = self.load_sprites()
        self.image = self.sprites[self.current_frame]
        self.rect = self.image.get_rect(center=center)

    def set_killed(self, killed: bool) -> None:
        """Switch between normal and eaten ghost sprites.

        Args:
            killed: Whether the ghost has been eaten.
        """
        if killed == self.killed:
            return

        center = self.rect.center
        self.killed = killed
        if killed:
            self.modifier = None
        self.sprites = self.load_sprites()
        self.image = self.sprites[self.current_frame]
        self.rect = self.image.get_rect(center=center)

    def update_animation(self) -> None:
        """Advance the ghost animation at its configured frame rate."""
        self.frame_count += 1

        if self.frame_count >= self.animation_speed:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % 2
            self.image = self.sprites[self.current_frame]

    def draw(self, screen: pygame.Surface) -> None:
        """Render the ghost sprite.

        Args:
            screen: Destination display surface.
        """
        screen.blit(self.image, self.rect)
