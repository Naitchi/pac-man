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
        super().__init__(game)
        s.maze = MazeGenerator((20, 20), perfect=False, seed=42).maze  # TODO remplacer les 20 20 et le 42 ? par une valeur dynamique
        s.wall_color = (0, 140, 220)
        s.floor_color = (0, 0, 0)
        s.pellet_color = (255, 255, 255)
        s.vertical_margin = 150
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
        s.nodes = [
            (
                s.offset_x + x * s.cell_size + s.cell_size // 2,
                s.offset_y + y * s.cell_size + s.cell_size // 2,
                cell_value,
            )
            for y, row in enumerate(s.maze)
            for x, cell_value in enumerate(row)
        ]
        s.spawn_player = s.get_middle_node()
        print(s.spawn_player)
        s.player = Player(*s.spawn_player)
        s.pellets = {   # TODO faire un deuxieme set pour les power-up pour simplifier l'algo pour lui donner des pouvoirs quand il en mange une ?
            (x, y)
            for y, row in enumerate(s.maze)
            for x, cell_value in enumerate(row)
            if cell_value != 15
        }

    def on_enter(self): pass

    def on_exit(self): pass

    def handle_event(self, event): pass

    def update(self, dt): pass

    def _has_wall(self, cell_value, wall_bit):
        return (cell_value & wall_bit) != 0

    def disable_pellet(self, x, y):
        self.pellets.discard((x, y))
        # TODO mettre une verif ici si max(pellets) == 0 alors on relance un playScene mais sans seed ?

    def enable_pellet(self, x, y):
        self.pellets.add((x, y))

    def _pellet_radius(self, x, y, cell_size):
        is_corner = (
            (x, y) == (0, 0)
            or (x, y) == (0, len(self.maze) - 1)
            or (x, y) == (len(self.maze[0]) - 1, 0)
            or (x, y) == (len(self.maze[0]) - 1, len(self.maze) - 1)
        )
        if is_corner:
            return max(4, cell_size // 5)
        return max(2, cell_size // 10)

    def get_middle_node(self):
        x_px, y_px, value = self.nodes[
            len(self.nodes)//2][len(self.nodes[0])//2]
        if value != 15:
            return (x_px, y_px)
        else:
            x_px, y_px, value = self.nodes[
                len(self.nodes)//2][(len(self.nodes[0])//2)+1]
            if value != 15:
                return (x_px, y_px)
            else:
                x_px, y_px, value = self.nodes[
                    len(self.nodes)//2][(len(self.nodes[0])//2)-1]
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
                        # TODO mettre ca dans un tableau au init puis reprendre les donnes ici, quand pac man se deplace il va juste de position en position, si il y a un input on le garde dans une variable (un mouvement max stocker (on pourrait mettre le nombre de bit comme ca on peut juste faire le bitshifting avec la valeur et pas besoin de passer par un intermediaire)  donc si il en fait un autre ca overwrite) ensuite regarde si dans la direction de l'input si il y a un mur ou non, jusqu'a ce qu'il y en ai un. donc il me faut deux variables une pour la direction actuel et une pour la prochaine.
                        (left + s.cell_size // 2,
                         top + s.cell_size // 2),
                        s._pellet_radius(x, y, s.cell_size),
                    )
                s.player.draw(screen)

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
