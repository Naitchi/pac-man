"""Pathfinding and movement strategies for autonomous ghosts."""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from abc import ABC, abstractmethod
import random
import time

from src.entities.ghost import Ghost

if TYPE_CHECKING:
    from src.scenes.play import PlayScene


class GhostIA(Ghost, ABC):
    """Base class for ghosts that navigate maze cells autonomously."""

    KILL_WAIT = 5

    def __init__(
        self,
        x: int,
        y: int,
        color: str,
        size: int,
        direction: str,
        build: bool,
        cell_x: int,
        cell_y: int,
        speed: int,
    ) -> None:
        """Initialize navigation state for a ghost.

        Args:
            x: Initial horizontal position in pixels.
            y: Initial vertical position in pixels.
            color: Ghost color used to select sprite assets.
            size: Square sprite size in pixels.
            direction: Initial visual direction.
            build: Whether resources are loaded from a packaged build.
            cell_x: Initial maze column.
            cell_y: Initial maze row.
            speed: Movement speed in pixels per frame.
        """
        super().__init__(x, y, color, size, direction, build)
        self.spawn_position: Tuple[int, int] = (x, y)
        self.spawn_cell: Tuple[int, int] = (cell_x, cell_y)
        self.cell_x: int = cell_x
        self.cell_y: int = cell_y
        self.target_cell: Optional[Tuple[int, int]] = None
        self.speed: int = speed
        self.kill_until: float = 0.0

    def update(self, scene: PlayScene) -> None:
        """Update visual state, choose a target, and move one frame.

        Args:
            scene: Active play scene containing maze and player state.
        """
        if self.killed:
            self.update_killed(scene)
            return

        modifier = None
        if scene.super_mode:
            modifier = "scared"
            if (
                scene.super_mode_time is not None
                and time.time() - scene.super_mode_time >= 8
                and int((time.time() - scene.super_mode_time) * 4) % 2 == 0
            ):
                modifier = "white"
        self.set_modifier(modifier)

        self.update_animation()
        if self.target_cell is None:
            if scene.super_mode:
                self.scared(scene)
            else:
                self.choose_target_cell(scene)
        self.move_to_target_cell(scene)

    def kill(self) -> None:
        """Mark the ghost as eaten and start its return to spawn."""
        self.kill_until = 0.0
        self.target_cell = None
        self.set_killed(True)

    def update_killed(self, scene: PlayScene) -> None:
        """Move an eaten ghost home and respawn it after a delay.

        Args:
            scene: Active play scene containing maze state.
        """
        self.update_animation()

        if self.rect.topleft == self.spawn_position:
            if self.kill_until == 0:
                self.kill_until = time.time() + self.KILL_WAIT
            elif time.time() >= self.kill_until:
                self.set_killed(False)
                self.set_modifier("scared" if scene.super_mode else None)
            return

        if self.target_cell is None:
            path = self.find_path(
                scene.maze,
                (self.cell_x, self.cell_y),
                self.spawn_cell,
            )
            self.target_cell = path[1] if len(path) > 1 else self.spawn_cell

        self.move_to_target_cell(scene)

    @abstractmethod
    def choose_target_cell(self, scene: PlayScene) -> None:
        """Choose the next adjacent maze cell.

        Args:
            scene: Active play scene containing maze and player state.
        """
        pass

    def scared(self, scene: PlayScene) -> None:
        """Choose the adjacent cell farthest from the player.

        Args:
            scene: Active play scene containing maze and player state.
        """
        if scene.player is None:
            self.target_cell = None
            return

        player_cell = self.pixel_to_cell(scene, scene.player.rect.center)
        neighbors = self.get_neighbors(scene.maze, self.cell_x, self.cell_y)
        self.target_cell = max(
            neighbors,
            key=lambda cell: (
                (cell[0] - player_cell[0]) ** 2
                + (cell[1] - player_cell[1]) ** 2
            ),
        )

    def move_to_target_cell(self, scene: PlayScene) -> None:
        """Move toward the currently selected target cell.

        Args:
            scene: Active play scene used for coordinate conversion.
        """
        if self.target_cell is None:
            return

        target_x, target_y = self.cell_to_pixel(scene, self.target_cell)

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
        """Return the ghost to its spawn position and normal state."""
        self.rect.topleft = self.spawn_position
        self.cell_x, self.cell_y = self.spawn_cell
        self.target_cell = None
        self.kill_until = 0.0
        self.set_modifier(None)
        self.set_killed(False)

    @staticmethod
    def pixel_to_cell(
        scene: PlayScene, position: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Convert a pixel position to maze coordinates.

        Args:
            scene: Active play scene defining maze offsets and cell size.
            position: Pixel coordinate to convert.

        Returns:
            Maze column and row containing the position.
        """
        return (
            (position[0] - scene.offset_x) // scene.cell_size,
            (position[1] - scene.offset_y) // scene.cell_size,
        )

    def cell_to_pixel(
        self, scene: PlayScene, cell: Tuple[int, int]
    ) -> Tuple[int, int]:
        """Convert a maze cell to the ghost's top-left pixel position.

        Args:
            scene: Active play scene defining maze offsets and cell size.
            cell: Maze column and row to convert.

        Returns:
            Top-left pixel position for the ghost sprite.
        """
        return (
            scene.offset_x
            + cell[0] * scene.cell_size
            + scene.cell_size // 2
            - self.size // 2,
            scene.offset_y
            + cell[1] * scene.cell_size
            + scene.cell_size // 2
            - self.size // 2,
        )

    @staticmethod
    def get_neighbors(
        maze: List[List[int]], cell_x: int, cell_y: int
    ) -> List[Tuple[int, int]]:
        """Return cells reachable from a maze position.

        Args:
            maze: Maze wall bitmasks indexed by row and column.
            cell_x: Current maze column.
            cell_y: Current maze row.

        Returns:
            Adjacent cells without a separating wall.
        """
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

    @classmethod
    def find_path(
        cls,
        maze: List[List[int]],
        start: Tuple[int, int],
        target: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """Find the shortest path between two maze cells.

        Args:
            maze: Maze wall bitmasks indexed by row and column.
            start: Starting maze cell.
            target: Destination maze cell.

        Returns:
            Ordered cells from start to target, or an empty list when no path
            exists.
        """
        queue = [start]
        visited = {start}
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}

        for current in queue:
            if current == target:
                path = [current]
                while current != start:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]

            for neighbor in cls.get_neighbors(maze, *current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return []


class GhostRed(GhostIA):
    """Ghost that directly follows the shortest path to the player."""

    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        direction: str,
        build: bool,
        cell_x: int,
        cell_y: int,
        speed: int,
    ) -> None:
        """Initialize the red chasing ghost.

        Args:
            x: Initial horizontal position in pixels.
            y: Initial vertical position in pixels.
            size: Square sprite size in pixels.
            direction: Initial visual direction.
            build: Whether resources are loaded from a packaged build.
            cell_x: Initial maze column.
            cell_y: Initial maze row.
            speed: Movement speed in pixels per frame.
        """
        super().__init__(
            x, y, "red", size, direction, build, cell_x, cell_y, speed
        )

    def choose_target_cell(self, scene: PlayScene) -> None:
        """Choose the first step on the shortest path to the player.

        Args:
            scene: Active play scene containing maze and player state.
        """
        if scene.player is None:
            self.target_cell = None
            return

        start = (self.cell_x, self.cell_y)
        target = self.pixel_to_cell(scene, scene.player.rect.center)
        path = self.find_path(scene.maze, start, target)
        self.target_cell = path[1] if len(path) > 1 else None


class GhostPink(GhostIA):
    """Ghost that targets cells ahead of the player's direction."""

    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        direction: str,
        build: bool,
        cell_x: int,
        cell_y: int,
        speed: int,
    ) -> None:
        """Initialize the pink ambush ghost.

        Args:
            x: Initial horizontal position in pixels.
            y: Initial vertical position in pixels.
            size: Square sprite size in pixels.
            direction: Initial visual direction.
            build: Whether resources are loaded from a packaged build.
            cell_x: Initial maze column.
            cell_y: Initial maze row.
            speed: Movement speed in pixels per frame.
        """
        super().__init__(
            x, y, "pink", size, direction, build, cell_x, cell_y, speed
        )

    def choose_target_cell(self, scene: PlayScene) -> None:
        """Choose a path toward a reachable cell ahead of the player.

        Args:
            scene: Active play scene containing maze and player state.
        """
        if scene.player is None:
            self.target_cell = None
            return

        start = (self.cell_x, self.cell_y)
        player_cell = self.pixel_to_cell(scene, scene.player.rect.center)
        direction = scene.player_direction or scene.player.direction
        dx = 0
        dy = 0
        if direction == 1:
            dy = -1
        elif direction == 2:
            dx = 1
        elif direction == 4:
            dy = 1
        elif direction == 8:
            dx = -1

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

        self.target_cell = path[1] if len(path) > 1 else None


class GhostBlue(GhostIA):
    """Ghost that patrols the four corners of the maze."""

    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        direction: str,
        build: bool,
        cell_x: int,
        cell_y: int,
        speed: int,
    ) -> None:
        """Initialize the blue corner-patrol ghost.

        Args:
            x: Initial horizontal position in pixels.
            y: Initial vertical position in pixels.
            size: Square sprite size in pixels.
            direction: Initial visual direction.
            build: Whether resources are loaded from a packaged build.
            cell_x: Initial maze column.
            cell_y: Initial maze row.
            speed: Movement speed in pixels per frame.
        """
        super().__init__(
            x, y, "blue", size, direction, build, cell_x, cell_y, speed
        )
        self.corner: int = 0

    def choose_target_cell(self, scene: PlayScene) -> None:
        """Choose the next step toward the current patrol corner.

        Args:
            scene: Active play scene containing maze state.
        """
        start = (self.cell_x, self.cell_y)
        right = len(scene.maze[0]) - 1
        bottom = len(scene.maze) - 1

        if self.corner == 0 and start == (0, 0):
            self.corner = 1
        elif self.corner == 1 and start == (right, 0):
            self.corner = 2
        elif self.corner == 2 and start == (right, bottom):
            self.corner = 3
        elif self.corner == 3 and start == (0, bottom):
            self.corner = 0

        if self.corner == 0:
            target = (0, 0)
        elif self.corner == 1:
            target = (right, 0)
        elif self.corner == 2:
            target = (right, bottom)
        else:
            target = (0, bottom)

        path = self.find_path(scene.maze, start, target)
        self.target_cell = path[1] if len(path) > 1 else None

    def reset_position(self) -> None:
        """Reset the ghost and restart its corner patrol."""
        super().reset_position()
        self.corner = 0


class GhostOrange(GhostIA):
    """Ghost that selects random reachable destinations."""

    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        direction: str,
        build: bool,
        cell_x: int,
        cell_y: int,
        speed: int,
    ) -> None:
        """Initialize the orange roaming ghost.

        Args:
            x: Initial horizontal position in pixels.
            y: Initial vertical position in pixels.
            size: Square sprite size in pixels.
            direction: Initial visual direction.
            build: Whether resources are loaded from a packaged build.
            cell_x: Initial maze column.
            cell_y: Initial maze row.
            speed: Movement speed in pixels per frame.
        """
        super().__init__(
            x, y, "orange", size, direction, build, cell_x, cell_y, speed
        )

    def choose_target_cell(self, scene: PlayScene) -> None:
        """Choose the first step toward a random accessible cell.

        Args:
            scene: Active play scene containing maze state.
        """
        maze = scene.maze
        height = len(maze)
        width = len(maze[0]) if height > 0 else 0

        accessible = [
            (cx, cy)
            for cy in range(height)
            for cx in range(width)
            if maze[cy][cx] != 15
        ]

        if not accessible:
            self.target_cell = None
            return

        candidates = [c for c in accessible if c != (self.cell_x, self.cell_y)]
        pool = candidates if candidates else accessible
        target = random.choice(pool)

        path = self.find_path(maze, (self.cell_x, self.cell_y), target)
        self.target_cell = path[1] if len(path) > 1 else None
