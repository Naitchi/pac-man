from __future__ import annotations
import pygame  # pyright: ignore[reportMissingImports]
from typing import List, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from src.scenes.play import PlayScene


class Ghost:
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
        build: bool
    ) -> None:
        self.color: str = color
        self.direction: str = direction
        self.size: int = size
        self.build: bool = build
        self.sprites: List[pygame.Surface] = self.load_sprites()
        self.current_frame: int = 0
        self.frame_count: int = 0
        self.animation_speed: int = 10

        self.image: pygame.Surface = self.sprites[0]
        self.rect: pygame.Rect = self.image.get_rect(x=x, y=y)

    def get_sprite_path(self, frame: int) -> str:
        base_path = "_internal/assets" if self.build else "src/entities/assets"

        modifiers = ["scared", "white"]

        if self.color in modifiers:
            return (f"{base_path}/modifier/{self.color}/"
                    f"{self.color}_{frame}.png")

        return (
            f"{base_path}/{self.color}/{self.direction}/"
            f"{self.color}_{self.direction}_{frame}.png"
        )

    def load_sprites(self) -> List[pygame.Surface]:
        sprites: List[pygame.Surface] = []

        for frame in range(1, 3):
            path = self.get_sprite_path(frame)
            image = pygame.image.load(path)
            sprites.append(
                pygame.transform.scale(image, (self.size, self.size)))

        return sprites

    def set_direction(self, direction: int | str) -> None:
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

    def update(self, scene: PlayScene | None = None) -> None:
        self.frame_count += 1

        if self.frame_count >= self.animation_speed:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % 2
            self.image = self.sprites[self.current_frame]

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)

    @staticmethod
    def pixel_to_cell(
        scene: PlayScene,
        pos: Tuple[int, int]
    ) -> Tuple[int, int]:
        return (
            (pos[0] - scene.offset_x) // scene.cell_size,
            (pos[1] - scene.offset_y) // scene.cell_size,
        )

    def reset_position(self) -> None:
        pass

    @staticmethod
    def cell_to_pixel(
        scene: PlayScene, cell_x: int, cell_y: int, size: int
    ) -> Tuple[int, int]:
        return (
            scene.offset_x
            + cell_x * scene.cell_size
            + scene.cell_size // 2
            - size // 2,
            scene.offset_y
            + cell_y * scene.cell_size
            + scene.cell_size // 2
            - size // 2,
        )

    @staticmethod
    def get_neighbors(
        maze: List[List[int]], cell_x: int, cell_y: int
    ) -> List[Tuple[int, int]]:
        neighbors: List[Tuple[int, int]] = []
        cell_value = maze[cell_y][cell_x]
        maze_height = len(maze)
        maze_width = len(maze[0])

        if cell_value & 1 == 0 and cell_y > 0:
            neighbors.append((cell_x, cell_y - 1))
        if cell_value & 2 == 0 and cell_x < maze_width - 1:
            neighbors.append((cell_x + 1, cell_y))
        if cell_value & 4 == 0 and cell_y < maze_height - 1:
            neighbors.append((cell_x, cell_y + 1))
        if cell_value & 8 == 0 and cell_x > 0:
            neighbors.append((cell_x - 1, cell_y))

        return neighbors

    @staticmethod
    def find_path(
        maze: List[List[int]], start: Tuple[int, int], target: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        queue: List[Tuple[int, int]] = [start]
        queue_index: int = 0
        visited = {start}
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

        while queue_index < len(queue):
            current = queue[queue_index]
            queue_index += 1

            if current == target:
                path = [current]
                while current != start:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            for neighbor in Ghost.get_neighbors(maze, current[0], current[1]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return []
