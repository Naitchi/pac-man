from typing import Literal, Optional, List, Tuple, Set
import pygame
import time
import sys

from src.entities.ia import (
    GhostIA,
    GhostPink,
    GhostRed,
    GhostBlue,
    GhostOrange,
)
from mazegenerator import MazeGenerator
from src.entities.player import Player
from .end_scene import EndScene
from src.game import Game
from .base import Scene


class PlayScene(Scene):
    WALL_TOP = 1
    WALL_RIGHT = 2
    WALL_BOTTOM = 4
    WALL_LEFT = 8

    def __init__(self, game: Game) -> None:
        # MAZE
        super().__init__(game)
        self.vertical_margin: int = 150
        self.map_finished: Optional[int] = None
        self.player: Optional[Player] = None
        self.ghosts: List[GhostIA] = []
        self.score: int = 0
        self.score_per_pellet: int = self.game.config.points_per_pacgum
        self.score_per_super_pellet: int = (
            self.game.config.points_per_super_pacgum
        )
        self.score_per_ghost: int = self.game.config.points_per_ghost
        self.wall_color: Tuple[int, int, int] = (0, 140, 220)
        self.floor_color: Tuple[int, int, int] = (0, 0, 0)
        self.pellet_color: Tuple[int, int, int] = (255, 255, 255)

        self.paused: bool = False

        # TIMER
        self.timer_max: int = self.game.config.level_max_time
        self.timer: Optional[float] = None
        self.timer_activated: bool = False
        self.timer_paused: bool = False
        self.timer_pause_elapsed: float = 0.0

        self.init_new_maze()

        # PLAYER
        self.cheat_invicibility: bool = False
        self.death_time: Optional[float] = None
        self.lives: int = self.game.config.lives
        self.hud_font: pygame.font.Font = pygame.font.Font(None, 36)
        self.super_mode_time: Optional[float] = None
        self.super_mode: bool = False
        self.super_mode_paused: bool = False
        self.super_mode_pause_elapsed: float = 0.0

    def init_new_maze(self) -> None:
        # MAZE
        if self.map_finished is None:
            self.map_finished = 0
        else:
            self.map_finished += 1
            self.timer = time.time()
        if (len(self.game.config.levels) <= 10
            and self.map_finished == 10) or (
            (
                len(self.game.config.levels) > 10
                and len(self.game.config.levels) == self.map_finished
            )
        ):
            self.game.change_scene(EndScene(self.game, self.score, True))
        try:
            self.maze: List[List[int]] = MazeGenerator(
                (
                    (
                        self.game.config.levels[
                            self.map_finished % len(self.game.config.levels)
                        ].width
                    ),
                    (
                        self.game.config.levels[
                            self.map_finished % len(self.game.config.levels)
                        ].height
                    ),
                ),
                perfect=False,
                seed=(self.game.config.seed if self.map_finished == 0 else -1),
            ).maze
        except Exception as e:
            print(f"Error generating maze: {e}", file=sys.stderr)
            sys.exit(1)
        self.maze_height: int = len(self.maze)
        self.maze_width: int = len(self.maze[0]) if self.maze_height else 0
        if self.maze_height == 0 or self.maze_width == 0:
            print("Error: no maze to show", file=sys.stderr)
            sys.exit(1)
        self.available_height: int = max(
            1, self.game.screen.get_height() - (self.vertical_margin * 2)
        )
        self.cell_size: int = min(
            self.game.screen.get_width() // self.maze_width,
            self.available_height // self.maze_height,
        )
        self.offset_x: int = (
            self.game.screen.get_width() - self.cell_size * self.maze_width
        ) // 2
        self.offset_y: int = self.vertical_margin + (
            (self.available_height - self.cell_size * self.maze_height) // 2
        )
        self.pellets: Set[Tuple[int, int]] = {
            (
                self.offset_x + x * self.cell_size + self.cell_size // 2,
                self.offset_y + y * self.cell_size + self.cell_size // 2,
            )
            for y, row in enumerate(self.maze)
            for x, cell_value in enumerate(row)
            if cell_value != 15
        }

        # PLAYER
        self.player_size: int = int(self.cell_size * 0.8)
        self.speed: int = int(self.cell_size * 0.0538)
        self.nodes: List[List[Tuple[int, int, int, int, int]]] = [
            [
                (
                    self.offset_x + x * self.cell_size + self.cell_size // 2,
                    self.offset_y + y * self.cell_size + self.cell_size // 2,
                    cell_value,
                    (
                        self.offset_x
                        + x * self.cell_size
                        + self.cell_size // 2
                        - self.player_size // 2
                    ),
                    (
                        self.offset_y
                        + y * self.cell_size
                        + self.cell_size // 2
                        - self.player_size // 2
                    ),
                )
                for x, cell_value in enumerate(row)
            ]
            for y, row in enumerate(self.maze)
        ]
        self.player_x, self.player_y = self.get_middle_node()
        self.delete_pellet(self.player_x, self.player_y)
        self.player_direction: Optional[Literal[1, 2, 4, 8]] = None
        self.player_next_direction: Optional[Literal[1, 2, 4, 8]] = None
        self.next_node_x: Optional[int] = None
        self.next_node_y: Optional[int] = None
        self.player = Player(
            self.player_x - self.player_size // 2,
            self.player_y - self.player_size // 2,
            self.game.config.build,
            self.player_size,
        )

        # GHOSTS
        _, _, _, red_x, red_y = self.nodes[0][0]
        _, _, _, pink_x, pink_y = self.nodes[0][self.maze_width - 1]
        _, _, _, orange_x, orange_y = self.nodes[self.maze_height - 1][0]
        _, _, _, blue_x, blue_y = self.nodes[self.maze_height - 1][
            self.maze_width - 1
        ]
        self.ghosts = [
            GhostRed(
                red_x,
                red_y,
                self.player_size,
                "down",
                self.game.config.build,
                0,
                0,
                self.speed - 1,
            ),
            GhostPink(
                pink_x,
                pink_y,
                self.player_size,
                "down",
                self.game.config.build,
                self.maze_width - 1,
                0,
                self.speed - 1,
            ),
            GhostOrange(
                orange_x,
                orange_y,
                self.player_size,
                "down",
                self.game.config.build,
                0,
                self.maze_height - 1,
                self.speed - 1,
            ),
            GhostBlue(
                blue_x,
                blue_y,
                self.player_size,
                "down",
                self.game.config.build,
                self.maze_width - 1,
                self.maze_height - 1,
                self.speed - 1,
            ),
        ]

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key in [pygame.K_UP, pygame.K_w]:
                self.player_next_direction = 1
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.player_next_direction = 2
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.player_next_direction = 4
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                self.player_next_direction = 8
            elif event.key == pygame.K_7:
                self.init_new_maze()
            elif event.key == pygame.K_8:
                self.cheat_invicibility = not self.cheat_invicibility
            elif event.key == pygame.K_9:
                if self.timer_paused:
                    self._resume_timer()
                else:
                    self._pause_timer()
            elif event.key == pygame.K_p:
                self.paused = not self.paused
                if self.paused:
                    self._pause_timer()
                    self._pause_super_mode()
                else:
                    self._resume_timer()
                    self._resume_super_mode()

    def get_values_from_node(self) -> Optional[Tuple[int, int, int, int, int]]:
        if self.player is None:
            return None
        px_x = self.player.rect.x
        px_y = self.player.rect.y
        for row in self.nodes:
            for (
                middle_x_px,
                middle_y_px,
                value,
                pac_man_cell_x,
                pac_man_cell_y,
            ) in row:
                if (
                    not self.next_node_x
                    and pac_man_cell_x == px_x
                    and not self.next_node_y
                    and pac_man_cell_y == px_y
                ):
                    return (
                        middle_x_px,
                        middle_y_px,
                        value,
                        pac_man_cell_x,
                        pac_man_cell_y,
                    )

                if (
                    self.next_node_x
                    and pac_man_cell_x == self.next_node_x
                    and self.next_node_y
                    and pac_man_cell_y == self.next_node_y
                ):
                    return (
                        middle_x_px,
                        middle_y_px,
                        value,
                        pac_man_cell_x,
                        pac_man_cell_y,
                    )
        return None

    def step(self) -> None:
        if self.player is None:
            return
        if self.player.dying:
            return
        if (
            self.player.rect.topleft != (self.next_node_x, self.next_node_y)
            and self.next_node_x is not None
            and self.next_node_y is not None
        ):
            if self.player_direction == 1 and not self.player.dying:
                self.player.rect.y = max(
                    self.next_node_y, self.player.rect.y - self.speed
                )
            elif self.player_direction == 2:
                self.player.rect.x = min(
                    self.next_node_x, self.player.rect.x + self.speed
                )
            elif self.player_direction == 4:
                self.player.rect.y = min(
                    self.next_node_y, self.player.rect.y + self.speed
                )
            elif self.player_direction == 8:
                self.player.rect.x = max(
                    self.next_node_x, self.player.rect.x - self.speed
                )
        elif self.player.rect.topleft == (
            self.next_node_x,
            self.next_node_y,
        ) or (not self.player_direction and self.player_next_direction):
            self.delete_pellet(*self.player.rect.center)
            if self.player_next_direction:
                self.player_direction = self.player_next_direction
                self.player_next_direction = None
                self.player.set_direction(self.player_direction)
            node_values = self.get_values_from_node()
            if node_values is None:
                return
            _, _, value, pac_man_cell_x, pac_man_cell_y = node_values
            if (
                self.player_direction is not None
                and (value & self.player_direction) == 0
            ):
                if self.player_direction == 1:
                    dx, dy = 0, -1
                elif self.player_direction == 2:
                    dx, dy = 1, 0
                elif self.player_direction == 4:
                    dx, dy = 0, 1
                elif self.player_direction == 8:
                    dx, dy = -1, 0
                else:
                    dx, dy = 0, 0
                self.next_node_x = pac_man_cell_x + dx * self.cell_size
                self.next_node_y = pac_man_cell_y + dy * self.cell_size
            else:
                self.player_direction = None

    def update_timer(self) -> None:
        if not self.timer_activated or self.timer is None or self.timer_paused:
            return
        elapsed = time.time() - self.timer
        if elapsed >= self.timer_max:
            self.game.change_scene(EndScene(self.game, self.score, False))

    def _pause_timer(self) -> None:
        if (
            self.timer_activated
            and self.timer is not None
            and not self.timer_paused
        ):
            self.timer_pause_elapsed = time.time() - self.timer
            self.timer_paused = True

    def _resume_timer(self) -> None:
        if self.timer_paused:
            self.timer = time.time() - self.timer_pause_elapsed
            self.timer_paused = False

    def _pause_super_mode(self) -> None:
        if (
            self.super_mode
            and self.super_mode_time is not None
            and not self.super_mode_paused
        ):
            self.super_mode_pause_elapsed = time.time() - self.super_mode_time
            self.super_mode_paused = True

    def _resume_super_mode(self) -> None:
        if self.super_mode_paused:
            self.super_mode_time = time.time() - self.super_mode_pause_elapsed
            self.super_mode_paused = False

    def update(self, dt: float) -> None:
        if self.paused:
            return
        if self.player is None:
            return
        self.player.update(dt)
        for ghost in self.ghosts:
            ghost.update(self)
        self.step()
        if not self.timer_activated:
            self._check_start_movement_timer()
        self.update_timer()
        self._disable_super_mode()
        self.check_ghost_collisions()

    def check_ghost_collisions(self) -> None:
        if self.player is None:
            return
        player_hitbox = self.player.rect.inflate(
            self.player_size // 7,
            -self.player_size // 7,
        )
        for ghost in self.ghosts:
            if ghost.killed:
                continue
            ghost_hitbox = ghost.rect.inflate(
                -ghost.size // 7,
                -ghost.size // 7,
            )
            if ghost_hitbox.colliderect(player_hitbox):
                if self.super_mode:
                    self.score += self.score_per_ghost
                    ghost.kill()
                    continue

                if not self.death_time and not self.cheat_invicibility:
                    self.player.death()
                    self.death_time = time.time()
                    return

                if self.death_time and time.time() - self.death_time >= 2:
                    self.death_time = None
                    self.lives -= 1
                    if self.lives == 0:
                        self.game.change_scene(
                            EndScene(self.game, self.score, False)
                        )
                        return
                    self.reset_round_positions()
                return

    def reset_round_positions(self) -> None:
        self.reset_player_position()
        for ghost in self.ghosts:
            ghost.reset_position()

    def reset_player_position(self) -> None:
        if self.player is None:
            return
        self.player.rect.topleft = (
            self.player_x - self.player_size // 2,
            self.player_y - self.player_size // 2,
        )
        self.player_direction = None
        self.player_next_direction = None
        self.player.dying = False
        self.next_node_x, self.next_node_y = (None, None)

    def _has_wall(self, cell_value: int, wall_bit: int) -> bool:
        return (cell_value & wall_bit) != 0

    def delete_pellet(self, x: int, y: int) -> None:
        try:
            self.pellets.remove((x, y))
            if (x, y) in [
                (
                    self.offset_x + x * self.cell_size + self.cell_size // 2,
                    self.offset_y + y * self.cell_size + self.cell_size // 2,
                )
                for (x, y) in [
                    (self.maze_width - 1, 0),
                    (0, 0),
                    (self.maze_width - 1, self.maze_height - 1),
                    (0, self.maze_height - 1),
                ]
            ]:
                self.score += self.score_per_super_pellet
                self.super_mode = True
                self.super_mode_time = time.time()
            else:
                self.score += self.score_per_pellet
            if not len(self.pellets):
                self.init_new_maze()
        except KeyError:
            pass

    def _disable_super_mode(self) -> None:
        if (
            self.super_mode
            and self.super_mode_time is not None
            and not self.super_mode_paused
            and time.time() - self.super_mode_time >= 10
        ):
            self.super_mode_time = None
            self.super_mode = False

    def _check_start_movement_timer(self) -> None:
        if self.player is None:
            return
        if self.player_direction is not None and all(
            getattr(g, "target_cell", None) is not None for g in self.ghosts
        ):
            self.timer = time.time()
            self.timer_activated = True

    def _pellet_radius(self, x: int, y: int, cell_size: int) -> int:
        is_corner = (
            (x, y) == (0, 0)
            or (x, y) == (0, len(self.maze) - 1)
            or (x, y) == (len(self.maze[0]) - 1, 0)
            or (x, y) == (len(self.maze[0]) - 1, len(self.maze) - 1)
        )
        if is_corner:
            return max(4, cell_size // 5)
        return max(2, cell_size // 10)

    def get_middle_node(self) -> Tuple[int, int]:
        x_px, y_px, value, _, _ = self.nodes[len(self.nodes) // 2][
            len(self.nodes[0]) // 2
        ]
        if value != 15:
            return (x_px, y_px)
        else:
            x_px, y_px, value, _, _ = self.nodes[len(self.nodes) // 2][
                (len(self.nodes[0]) // 2) - 1
            ]
            if value != 15:
                return (x_px, y_px)
            else:
                x_px, y_px, value, _, _ = self.nodes[len(self.nodes) // 2][
                    (len(self.nodes[0]) // 2) + 1
                ]
                if value != 15:
                    return (x_px, y_px)
                else:
                    print(
                        "Error: was not able to spawn Pac-Man",
                        file=sys.stderr,
                    )
                    sys.exit(1)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(self.floor_color)
        wall_thickness = max(2, self.cell_size // 8)

        for y, row in enumerate(self.maze):
            for x, cell_value in enumerate(row):
                left = self.offset_x + x * self.cell_size
                top = self.offset_y + y * self.cell_size
                right = left + self.cell_size
                bottom = top + self.cell_size

                pygame.draw.rect(
                    screen,
                    self.floor_color,
                    pygame.Rect(left, top, self.cell_size, self.cell_size),
                )
                pellet_coords = (
                    left + self.cell_size // 2,
                    top + self.cell_size // 2,
                )
                if pellet_coords in self.pellets:
                    pygame.draw.circle(
                        screen,
                        self.pellet_color,
                        pellet_coords,
                        self._pellet_radius(x, y, self.cell_size),
                    )

                if self._has_wall(cell_value, self.WALL_TOP):
                    pygame.draw.line(
                        screen,
                        self.wall_color,
                        (left, top),
                        (right, top),
                        wall_thickness,
                    )
                if self._has_wall(cell_value, self.WALL_RIGHT):
                    pygame.draw.line(
                        screen,
                        self.wall_color,
                        (right, top),
                        (right, bottom),
                        wall_thickness,
                    )
                if self._has_wall(cell_value, self.WALL_BOTTOM):
                    pygame.draw.line(
                        screen,
                        self.wall_color,
                        (left, bottom),
                        (right, bottom),
                        wall_thickness,
                    )
                if self._has_wall(cell_value, self.WALL_LEFT):
                    pygame.draw.line(
                        screen,
                        self.wall_color,
                        (left, top),
                        (left, bottom),
                        wall_thickness,
                    )
        for ghost in self.ghosts:
            ghost.draw(screen)
        if self.player is not None:
            self.player.draw(screen)
        self.draw_hud(screen)

    def draw_hud(self, screen: pygame.Surface) -> None:
        white = (255, 255, 255)
        y = self.offset_y

        lives_text = self.hud_font.render(f"Lives: {self.lives}", True, white)
        score_text = self.hud_font.render(f"Score: {self.score}", True, white)
        level_text = self.hud_font.render(
            f"Level: {self.map_finished}", True, white)

        if self.timer_activated and self.timer is not None:
            if self.timer_paused:
                remaining = max(
                    0, int(self.timer_max - self.timer_pause_elapsed)
                )
                timer_text = self.hud_font.render(
                    f"Timer: {remaining:02d}s (Paused)", True, (255, 200, 0)
                )
            else:
                remaining = max(
                    0, int(self.timer_max - (time.time() - self.timer))
                )
                timer_text = self.hud_font.render(
                    f"Timer: {remaining:02d}s", True, white
                )
        else:
            timer_text = self.hud_font.render("Timer: s", True, white)

        shortcut_lines = [
            "Arrows: move",
            "7: Skip Level",
            "8: Invincibility",
            "9: Pause timer",
            "Esc: quit",
        ]

        screen.blit(lives_text, (10, y))
        screen.blit(score_text, (10, y + 30))
        screen.blit(level_text, (10, y + 60))
        screen.blit(timer_text, (10, y + 90))

        shortcut_y = y
        shortcut_x = max(260, self.game.screen.get_width() - 260)
        for index, line in enumerate(shortcut_lines):
            shortcut_text = self.hud_font.render(line, True, white)
            screen.blit(shortcut_text, (shortcut_x, shortcut_y + index * 28))
        self.draw_pause_menu(screen)

    def draw_pause_menu(self, screen: pygame.Surface) -> None:
        if self.paused:
            overlay_w, overlay_h = 320, 140
            overlay_x = self.game.screen.get_width() // 2 - overlay_w // 2
            overlay_y = self.game.screen.get_height() // 2 - overlay_h // 2

            pygame.draw.rect(
                screen, (0, 0, 0), (overlay_x, overlay_y, overlay_w, overlay_h)
            )
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                (overlay_x, overlay_y, overlay_w, overlay_h),
                2,
            )

            title_font = pygame.font.Font(None, 52)
            small_font = pygame.font.Font(None, 30)

            title = title_font.render("PAUSED", True, (255, 200, 0))
            resume = small_font.render(
                "Press P to resume", True, (255, 255, 255)
            )
            quit_text = small_font.render(
                "Press Escape to quit", True, (255, 255, 255)
            )

            screen.blit(
                title,
                (
                    overlay_x + overlay_w // 2 - title.get_width() // 2,
                    overlay_y + 20,
                ),
            )
            screen.blit(
                resume,
                (
                    overlay_x + overlay_w // 2 - resume.get_width() // 2,
                    overlay_y + 75,
                ),
            )
            screen.blit(
                quit_text,
                (
                    (overlay_x + overlay_w // 2 - quit_text.get_width() // 2),
                    overlay_y + 105,
                ),
            )
