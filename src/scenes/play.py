import sys
import pygame
from src.entities.ia import PinkGhost, RedGhost
from src.entities.player import Player
from .base import Scene
from .end_scene import EndScene
from mazegenerator import MazeGenerator
import time


class PlayScene(Scene):
    WALL_TOP = 1
    WALL_RIGHT = 2
    WALL_BOTTOM = 4
    WALL_LEFT = 8

    def __init__(s, game):
        # MAZE
        super().__init__(game)
        s.vertical_margin = 150  # TODO un pourcentage a la place ?
        s.map_finished = None
        s.player = None
        s.ghosts = None
        s.init_new_maze()
        s.wall_color = (0, 140, 220)
        s.floor_color = (0, 0, 0)
        s.pellet_color = (255, 255, 255)

        # PLAYER
        s.cheat_invicibility = False
        s.death_time = None
        s.score = 0
        s.lives = s.game.config.lives
        s.hud_font = pygame.font.Font(None, 36)

    def init_new_maze(s):
        # TODO il faudrai rajouter des verifications dans le config pour pas qu'ils puissent mettre des labyrinth trop petit pour que tout le monde spawn dedans.
        # genre 5x5 minimum et 25x25 max?
        # MAZE
        if s.map_finished is None:
            s.map_finished = 0
        else:
            s.map_finished += 1
        if ((len(s.game.config.levels) <= 10 and s.map_finished == 10)
                or ((len(s.game.config.levels) > 10
                     and len(s.game.config.levels) == s.map_finished))):
            s.game.change_scene(EndScene(s.game, s.score, True))
        s.maze = MazeGenerator(
            ((s.game.config.levels[s.map_finished
                                   % len(s.game.config.levels)].width),
             (s.game.config.levels[s.map_finished
                                   % len(s.game.config.levels)].height)),
            perfect=False,
            seed=(42 if s.map_finished == 0 else -1)
        ).maze
        s.maze_height = len(s.maze)
        s.maze_width = len(s.maze[0]) if s.maze_height else 0
        if s.maze_height == 0 or s.maze_width == 0:
            print("Error: no maze to show")
            sys.exit()
        s.available_height = max(
            1, s.game.screen.get_height() - (s.vertical_margin * 2))
        s.cell_size = min(
            s.game.screen.get_width() // s.maze_width,
            s.available_height // s.maze_height,
        )
        s.offset_x = (
            s.game.screen.get_width() - s.cell_size * s.maze_width
        ) // 2
        s.offset_y = s.vertical_margin + (
            (s.available_height - s.cell_size * s.maze_height) // 2
        )
        # TODO: considérer un second set pour les power-ups
        # (simplifie la gestion des pouvoirs quand on en mange un)
        s.pellets = {
            (s.offset_x + x * s.cell_size + s.cell_size // 2,
             s.offset_y + y * s.cell_size + s.cell_size // 2)
            for y, row in enumerate(s.maze)
            for x, cell_value in enumerate(row)
            if cell_value != 15
        }

        # PLAYER
        s.player_size = int(s.cell_size * 0.8)
        s.speed = int(s.cell_size * 0.0538)
        s.nodes = [
            [
                (
                    s.offset_x + x * s.cell_size + s.cell_size // 2,
                    s.offset_y + y * s.cell_size + s.cell_size // 2,
                    cell_value,
                    (s.offset_x + x * s.cell_size +
                        s.cell_size // 2 - s.player_size // 2),
                    (s.offset_y + y * s.cell_size +
                        s.cell_size // 2 - s.player_size // 2),
                )
                for x, cell_value in enumerate(row)
            ]
            for y, row in enumerate(s.maze)
        ]
        s.player_x, s.player_y = s.get_middle_node()
        s.disable_pellet(s.player_x, s.player_y)
        s.player_direction = None
        s.player_next_direction = None
        s.next_node_x, s.next_node_y = (None, None)
        s.player = Player(
            s.player_x - s.player_size // 2,
            s.player_y - s.player_size // 2,
            s.game.config.build,
            s.player_size)

        # GHOSTS
        _, _, _, ghost_x, ghost_y = s.nodes[0][0]
        _, _, _, pink_x, pink_y = s.nodes[0][s.maze_width - 1]
        s.ghosts = [
            RedGhost(
                ghost_x,
                ghost_y,
                s.player_size,
                "down",
                s.game.config.build,
                s.cell_size,
                0,
                0,
                s.speed - 1),
            PinkGhost(
                pink_x,
                pink_y,
                s.player_size,
                "down",
                s.game.config.build,
                s.cell_size,
                s.maze_width - 1,
                0,
                s.speed - 1)]

    def on_enter(s): pass

    def on_exit(s): pass

    def handle_event(s, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                s.game.running = False
            elif event.key == pygame.K_UP:
                s.player_next_direction = 1
            elif event.key == pygame.K_RIGHT:
                s.player_next_direction = 2
            elif event.key == pygame.K_DOWN:
                s.player_next_direction = 4
            elif event.key == pygame.K_LEFT:
                s.player_next_direction = 8
            elif event.key == pygame.K_7:  # TODO mettre une legende pour ca
                s.init_new_maze()
            elif event.key == pygame.K_8:  # TODO mettre une legende pour ca
                s.cheat_invicibility = not s.cheat_invicibility

    def get_values_from_node(s):
        px_x = s.player.rect.x
        px_y = s.player.rect.y
        for row in s.nodes:
            for (
                middle_x_px,
                middle_y_px,
                value,
                pac_man_cell_x,
                pac_man_cell_y,
            ) in row:
                if (
                    not s.next_node_x
                    and pac_man_cell_x == px_x
                    and not s.next_node_y
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
                    s.next_node_x
                    and pac_man_cell_x == s.next_node_x
                    and s.next_node_y
                    and pac_man_cell_y == s.next_node_y
                ):
                    return (
                        middle_x_px,
                        middle_y_px,
                        value,
                        pac_man_cell_x,
                        pac_man_cell_y,
                    )

    def step(s):
        if s.player.dying:
            return
        if (s.player.rect.topleft != (s.next_node_x, s.next_node_y)
                and s.next_node_x is not None and s.next_node_y is not None):
            if s.player_direction == 1 and not s.player.dying:
                s.player.rect.y = max(s.next_node_y, s.player.rect.y - s.speed)
            elif s.player_direction == 2:
                s.player.rect.x = min(s.next_node_x, s.player.rect.x + s.speed)
            elif s.player_direction == 4:
                s.player.rect.y = min(s.next_node_y, s.player.rect.y + s.speed)
            elif s.player_direction == 8:
                s.player.rect.x = max(s.next_node_x, s.player.rect.x - s.speed)
        elif (s.player.rect.topleft == (s.next_node_x, s.next_node_y) or
              (not s.player_direction and s.player_next_direction)):
            s.disable_pellet(*s.player.rect.center)
            if s.player_next_direction:
                s.player_direction = s.player_next_direction
                s.player_next_direction = None
                s.player.set_direction(s.player_direction)
            (_, _, value, pac_man_cell_x,
             pac_man_cell_y) = s.get_values_from_node()
            if s.player_direction is not None and (value & s.player_direction) == 0:
                if s.player_direction == 1:
                    dx, dy = 0, -1
                elif s.player_direction == 2:
                    dx, dy = 1, 0
                elif s.player_direction == 4:
                    dx, dy = 0, 1
                elif s.player_direction == 8:
                    dx, dy = -1, 0
                s.next_node_x = pac_man_cell_x + dx * s.cell_size
                s.next_node_y = pac_man_cell_y + dy * s.cell_size
            else:
                s.player_direction = None

    def update(s, dt):
        s.player.update(dt)
        for ghost in s.ghosts:
            ghost.update(s)
        s.step()
        if not s.cheat_invicibility:
            s.check_ghost_collisions()

    def check_ghost_collisions(s):
        for ghost in s.ghosts:
            if ghost.rect.colliderect(s.player.rect):
                if not s.death_time:
                    s.player.death()
                    s.death_time = time.time()
                    return

                if time.time() - s.death_time >= 2:
                    s.death_time = None
                    s.lives -= 1
                    if s.lives == 0:
                        s.game.change_scene(EndScene(s.game, s.score, False))
                        return
                    s.reset_round_positions()
                return

    def reset_round_positions(s):
        s.reset_player_position()
        for ghost in s.ghosts:
            ghost.reset_position()

    def reset_player_position(s):
        s.player.rect.topleft = (
            s.player_x - s.player_size // 2,
            s.player_y - s.player_size // 2,
        )
        s.player_direction = None
        s.player_next_direction = None
        s.player.dying = False
        s.next_node_x, s.next_node_y = (None, None)

    def _has_wall(s, cell_value, wall_bit):
        return (cell_value & wall_bit) != 0

    def disable_pellet(s, x, y):
        s.pellets.discard((x, y))
        if not len(s.pellets):
            s.init_new_maze()

    def enable_pellet(s, x, y):
        s.pellets.add((x, y))

    def _pellet_radius(s, x, y, cell_size):
        is_corner = (
            (x, y) == (0, 0)
            or (x, y) == (0, len(s.maze) - 1)
            or (x, y) == (len(s.maze[0]) - 1, 0)
            or (x, y) == (len(s.maze[0]) - 1, len(s.maze) - 1)
        )
        if is_corner:
            return max(4, cell_size // 5)
        return max(2, cell_size // 10)

    def get_middle_node(s):
        x_px, y_px, value, _, _ = s.nodes[
            len(s.nodes) // 2][len(s.nodes[0]) // 2]
        if value != 15:
            return (x_px, y_px)
        else:
            x_px, y_px, value, _, _ = s.nodes[
                len(s.nodes) // 2][(len(s.nodes[0]) // 2) - 1]
            if value != 15:
                return (x_px, y_px)
            else:
                x_px, y_px, value, _, _ = s.nodes[
                    len(s.nodes) // 2][(len(s.nodes[0]) // 2) + 1]
                if value != 15:
                    return (x_px, y_px)
                else:
                    print("Error: was not eable to spawn in pac-man")
                    sys.exit()

    def draw(s, screen):
        screen.fill(s.floor_color)
        wall_thickness = max(2, s.cell_size // 8)

        for y, row in enumerate(s.maze):
            for x, cell_value in enumerate(row):
                left = s.offset_x + x * s.cell_size
                top = s.offset_y + y * s.cell_size
                right = left + s.cell_size
                bottom = top + s.cell_size

                pygame.draw.rect(
                    screen,
                    s.floor_color,
                    pygame.Rect(left, top, s.cell_size, s.cell_size),
                )
                pellet_coords = (left + s.cell_size // 2,
                                 top + s.cell_size // 2)
                if pellet_coords in s.pellets:
                    pygame.draw.circle(
                        screen,
                        s.pellet_color,
                        pellet_coords,
                        s._pellet_radius(x, y, s.cell_size),
                    )

                if s._has_wall(cell_value, s.WALL_TOP):
                    pygame.draw.line(screen, s.wall_color,
                                     (left, top), (right, top), wall_thickness)
                if s._has_wall(cell_value, s.WALL_RIGHT):
                    pygame.draw.line(
                        screen,
                        s.wall_color,
                        (right, top),
                        (right, bottom),
                        wall_thickness)
                if s._has_wall(cell_value, s.WALL_BOTTOM):
                    pygame.draw.line(
                        screen,
                        s.wall_color,
                        (left, bottom),
                        (right, bottom),
                        wall_thickness)
                if s._has_wall(cell_value, s.WALL_LEFT):
                    pygame.draw.line(
                        screen,
                        s.wall_color,
                        (left, top),
                        (left, bottom),
                        wall_thickness)
        for ghost in s.ghosts:
            ghost.draw(screen)
        s.player.draw(screen)
        s.draw_hud(screen)

    def draw_hud(s, screen):
        lives_text = s.hud_font.render(
            f"Lives: {s.lives}",
            True,
            (255, 255, 255))
        screen.blit(lives_text, (10, s.offset_y))
