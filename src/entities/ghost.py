import pygame


class Ghost:
    DIRECTIONS = {
        1: "up",
        2: "right",
        4: "down",
        8: "left",
    }

    def __init__(s, x, y, color, size, direction, build):
        s.color = color
        s.direction = direction
        s.size = size
        s.build = build
        s.sprites = s.load_sprites()
        s.current_frame = 0
        s.frame_count = 0
        s.animation_speed = 10

        s.image = s.sprites[0]
        s.rect = s.image.get_rect(x=x, y=y)

    def get_sprite_path(s, frame):
        base_path = "_internal/assets" if s.build else "src/entities/assets"

        modifiers = ["scared", "white"]

        if s.color in modifiers:
            return (
                f"{base_path}/modifier/{s.color}/"
                f"{s.color}_{frame}.png"
            )

        return (
            f"{base_path}/{s.color}/{s.direction}/"
            f"{s.color}_{s.direction}_{frame}.png"
        )

    def load_sprites(s):
        sprites = []

        for frame in range(1, 3):
            path = s.get_sprite_path(frame)
            image = pygame.image.load(path)
            sprites.append(pygame.transform.scale(image, (s.size, s.size)))

        return sprites

    def set_direction(s, direction):
        direction = s.DIRECTIONS.get(direction, direction)
        if direction == s.direction:
            return

        center = s.rect.center
        s.direction = direction
        s.sprites = s.load_sprites()
        s.current_frame %= 2
        s.image = s.sprites[s.current_frame]
        s.rect = s.image.get_rect(center=center)

    def update(s):
        s.frame_count += 1

        if s.frame_count >= s.animation_speed:
            s.frame_count = 0
            s.current_frame = (s.current_frame + 1) % 2
            s.image = s.sprites[s.current_frame]

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    @staticmethod
    def pixel_to_cell(scene, pos):
        return (
            (pos[0] - scene.offset_x) // scene.cell_size,
            (pos[1] - scene.offset_y) // scene.cell_size,
        )

    @staticmethod
    def cell_to_pixel(scene, cell_x, cell_y, size):
        return (
            scene.offset_x + cell_x * scene.cell_size +
            scene.cell_size // 2 - size // 2,
            scene.offset_y + cell_y * scene.cell_size +
            scene.cell_size // 2 - size // 2,
        )

    @staticmethod
    def get_neighbors(maze, cell_x, cell_y):
        neighbors = []
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
    def find_path(maze, start, target):
        queue = [start]
        queue_index = 0
        visited = {start}
        came_from = {}

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
