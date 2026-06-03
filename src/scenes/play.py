import sys
import pygame
from src.entities.player import Player
from .base import Scene
from mazegenerator import MazeGenerator


class PlayScene(Scene):
    WALL_TOP = 1
    WALL_RIGHT = 2
    WALL_BOTTOM = 4
    WALL_LEFT = 8

    def __init__(s, game):
        # MAZE
        super().__init__(game)
        # TODO remplacer les 20 20 et le 42 ? par une valeur dynamique
        s.maze = MazeGenerator((20, 20), perfect=False, seed=42).maze
        s.wall_color = (0, 140, 220)
        s.floor_color = (0, 0, 0)
        s.pellet_color = (255, 255, 255)
        s.vertical_margin = 150  # TODO un pourcentage a la place ?
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
            (x, y)
            for y, row in enumerate(s.maze)
            for x, cell_value in enumerate(row)
            if cell_value != 15
        }
        print(s.pellets)

        # PLAYER
        s.player_direction = None
        s.player_next_direction = None
        s.player_size = int(s.cell_size * 0.8)
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
        # en soit la j'ai ma valeur et je pourrais comparer a ca directe au coordonnes de la prochaine case (selon la direction) pour eviter de surcharger de calcul
        s.player_x, s.player_y = s.get_middle_node()
        s.next_node_x, s.next_node_y = (None, None)
        s.player = Player(
            s.player_x - s.player_size // 2,
            s.player_y - s.player_size // 2,
            s.player_size)

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

    def update(s, dt):
        s.player.update(dt)
        # TODO tout mettre dans une fonction :
        if s.player.rect.topleft != (s.next_node_x, s.next_node_y) and s.next_node_x:
            if s.player_direction == 1:
                s.player.rect.y -= 1
            if s.player_direction == 2:
                s.player.rect.x += 1
            if s.player_direction == 4:
                s.player.rect.y += 1
            if s.player_direction == 8:
                s.player.rect.x -= 1
        elif (s.player.rect.topleft == (s.next_node_x, s.next_node_y) or
              (not s.player_direction and s.player_next_direction)):
            if s.player_next_direction:
                s.player_direction = s.player_next_direction
                s.player_next_direction = None
                s.player.set_direction(s.player_direction)
            (middle_x_px, middle_y_px, value, pac_man_cell_x,
             pac_man_cell_y) = s.get_values_from_node()
            if value & s.player_direction == 0:
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

    def _has_wall(s, cell_value, wall_bit):
        return (cell_value & wall_bit) != 0

    def disable_pellet(s, x, y):
        s.pellets.discard((x, y))
        # TODO mettre une verif ici si max(pellets) == 0 alors on relance un playScene mais sans seed ?

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
            len(s.nodes)//2][len(s.nodes[0])//2]
        if value != 15:
            return (x_px, y_px)
        else:
            x_px, y_px, value, _, _ = s.nodes[
                len(s.nodes)//2][(len(s.nodes[0])//2)-1]
            if value != 15:
                return (x_px, y_px)
            else:
                x_px, y_px, value, _, _ = s.nodes[
                    len(s.nodes)//2][(len(s.nodes[0])//2)+1]
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

                if (x, y) in s.pellets:
                    pygame.draw.circle(
                        screen,
                        s.pellet_color,
                        # TODO quand pac man se deplace il va juste de position en position, si il y a un input on le garde dans une variable (un mouvement max stocker (on pourrait mettre le nombre de bit comme ca on peut juste faire le bitshifting avec la valeur et pas besoin de passer par un intermediaire)  donc si il en fait un autre ca overwrite) ensuite regarde si dans la direction de l'input si il y a un mur ou non, jusqu'a ce qu'il y en ai un.
                        (left + s.cell_size // 2,
                         top + s.cell_size // 2),
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
        s.player.draw(screen)
