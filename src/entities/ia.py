from __future__ import annotations
from typing import Optional, Tuple, TYPE_CHECKING

from src.entities.ghost import Ghost

if TYPE_CHECKING:
    from src.scenes.play import PlayScene


class RedGhost(Ghost):
    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        direction: str,
        build: bool,
        cell_size: int,
        cell_x: int,
        cell_y: int,
        speed: int,
    ) -> None:
        super().__init__(x, y, "red", size, direction, build)
        self.cell_size: int = cell_size
        self.spawn_x: int = x
        self.spawn_y: int = y
        self.spawn_cell_x: int = cell_x
        self.spawn_cell_y: int = cell_y
        self.cell_x: int = cell_x
        self.cell_y: int = cell_y
        self.target_cell: Optional[Tuple[int, int]] = None
        self.speed: int = speed

    def update(self, scene: PlayScene | None = None) -> None:
        super().update()
        if self.target_cell is None:
            self.choose_target_cell(scene)
        self.move_to_target_cell(scene)

    def choose_target_cell(self, scene: PlayScene | None) -> None:
        if scene is None or scene.player is None:
            self.target_cell = None
            return
        start = (self.cell_x, self.cell_y)
        target = self.pixel_to_cell(scene, scene.player.rect.center)
        path = self.find_path(scene.maze, start, target)

        if len(path) > 1:
            self.target_cell = path[1]
        else:
            self.target_cell = None

    def move_to_target_cell(self, scene: PlayScene | None) -> None:
        if scene is None:
            return
        if self.target_cell is None:
            return

        target_x, target_y = self.cell_to_pixel(
            scene,
            self.target_cell[0],
            self.target_cell[1],
            self.size,
        )

        if self.rect.x < target_x:
            self.set_direction("right")
            self.rect.x = min(target_x, self.rect.x + self.speed)
        elif self.rect.x > target_x:
            self.set_direction("left")
            self.rect.x = max(target_x, self.rect.x - self.speed)
        elif self.rect.y < target_y:
            self.set_direction("down")
            self.rect.y = min(target_y, self.rect.y + self.speed)
        elif self.rect.y > target_y:
            self.set_direction("up")
            self.rect.y = max(target_y, self.rect.y - self.speed)

        if self.rect.topleft == (target_x, target_y):
            self.cell_x, self.cell_y = self.target_cell
            self.target_cell = None

    def reset_position(self) -> None:
        self.rect.topleft = (self.spawn_x, self.spawn_y)
        self.cell_x = self.spawn_cell_x
        self.cell_y = self.spawn_cell_y
        self.target_cell = None


class PinkGhost(RedGhost):
    DIRECTION_OFFSET = {
        1: (0, -1),
        2: (1, 0),
        4: (0, 1),
        8: (-1, 0),
    }

    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        direction: str,
        build: bool,
        cell_size: int,
        cell_x: int,
        cell_y: int,
        speed: int,
    ) -> None:
        Ghost.__init__(self, x, y, "pink", size, direction, build)
        self.cell_size: int = cell_size
        self.spawn_x: int = x
        self.spawn_y: int = y
        self.spawn_cell_x: int = cell_x
        self.spawn_cell_y: int = cell_y
        self.cell_x: int = cell_x
        self.cell_y: int = cell_y
        self.target_cell: Optional[Tuple[int, int]] = None
        self.speed: int = speed

    def choose_target_cell(self, scene: PlayScene | None) -> None:
        if scene is None or scene.player is None:
            self.target_cell = None
            return
        start = (self.cell_x, self.cell_y)
        player_cell = self.pixel_to_cell(scene, scene.player.rect.center)
        direction = scene.player_direction or scene.player.direction
        dx, dy = self.DIRECTION_OFFSET.get(direction, (1, 0))
        target = player_cell
        for _ in range(4):
            next_cell = (target[0] + dx, target[1] + dy)
            neighbors = self.get_neighbors(scene.maze, target[0], target[1])
            if next_cell not in neighbors:
                break
            target = next_cell
        path = self.find_path(scene.maze, start, target)

        if len(path) <= 1:
            path = self.find_path(scene.maze, start, player_cell)

        if len(path) > 1:
            self.target_cell = path[1]
        else:
            self.target_cell = None
