import pygame
from .base import Scene
from mazegenerator import MazeGenerator


class PlayScene(Scene):
    WALL_TOP = 1
    WALL_RIGHT = 2
    WALL_BOTTOM = 4
    WALL_LEFT = 8

    def __init__(self, game):
        super().__init__(game)
        self.maze = MazeGenerator((20, 20), perfect=False, seed=42).maze
        self.wall_color = (0, 140, 220)
        self.floor_color = (0, 0, 0)
        self.pellet_color = (255, 255, 255)
        self.pellets = {   # TODO faire un deuxieme set pour les power-up pour simplifier l'algo pour lui donner des pouvoirs quand il en mange une ?
            (x, y)
            for y, row in enumerate(self.maze)
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

    def draw(self, screen):
        screen.fill(self.floor_color)

        maze_height = len(self.maze)
        maze_width = len(self.maze[0]) if maze_height else 0
        if maze_height == 0 or maze_width == 0:
            return

        vertical_margin = 150
        available_height = max(1, screen.get_height() - (vertical_margin * 2))

        cell_size = min(
            screen.get_width() // maze_width,
            available_height // maze_height,
        )
        offset_x = (screen.get_width() - cell_size * maze_width) // 2
        offset_y = vertical_margin + (
            (available_height - cell_size * maze_height) // 2
        )
        wall_thickness = max(2, cell_size // 8)

        for y, row in enumerate(self.maze):
            for x, cell_value in enumerate(row):
                left = offset_x + x * cell_size
                top = offset_y + y * cell_size
                right = left + cell_size
                bottom = top + cell_size

                pygame.draw.rect(
                    screen,
                    self.floor_color,
                    pygame.Rect(left, top, cell_size, cell_size),
                )

                if (x, y) in self.pellets:
                    pygame.draw.circle(
                        screen,
                        self.pellet_color,
                        # TODO mettre ca dans un tableau, quand pac man se deplace il va juste de position en position, si il y a un input on le garde dans une variable (un mouvement max stocker (on pourrait mettre le nombre de bit comme ca on peut juste faire le bitshifting avec la valeur et pas besoin de passer par un intermediaire)  donc si il en fait un autre ca overwrite) ensuite regarde si dans la direction de l'input si il y a un mur ou non, jusqu'a ce qu'il y en ai un. donc il me faut deux variables une pour la direction actuel et une pour la prochaine.
                        (left + cell_size // 2, top + cell_size // 2),
                        self._pellet_radius(x, y, cell_size),
                    )

                if self._has_wall(cell_value, self.WALL_TOP):
                    pygame.draw.line(screen, self.wall_color,
                                     (left, top), (right, top), wall_thickness)
                if self._has_wall(cell_value, self.WALL_RIGHT):
                    pygame.draw.line(
                        screen,
                        self.wall_color,
                        (right, top),
                        (right, bottom),
                        wall_thickness)
                if self._has_wall(cell_value, self.WALL_BOTTOM):
                    pygame.draw.line(
                        screen,
                        self.wall_color,
                        (left, bottom),
                        (right, bottom),
                        wall_thickness)
                if self._has_wall(cell_value, self.WALL_LEFT):
                    pygame.draw.line(
                        screen,
                        self.wall_color,
                        (left, top),
                        (left, bottom),
                        wall_thickness)
