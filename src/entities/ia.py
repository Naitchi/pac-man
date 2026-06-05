from src.entities.ghost import Ghost


class RedGhost(Ghost):
    def __init__(s, x, y, size, direction, build, cell_size, cell_x, cell_y):
        super().__init__(x, y, "red", size, direction, build)
        s.cell_size = cell_size
        s.spawn_x = x
        s.spawn_y = y
        s.spawn_cell_x = cell_x
        s.spawn_cell_y = cell_y
        s.cell_x = cell_x
        s.cell_y = cell_y
        s.target_cell = None
        s.speed = 5

    def update(s, scene):
        super().update()
        if s.target_cell is None:
            s.choose_target_cell(scene)
        s.move_to_target_cell(scene)

    def choose_target_cell(s, scene):
        start = (s.cell_x, s.cell_y)
        target = s.pixel_to_cell(scene, scene.player.rect.center)
        path = s.find_path(scene.maze, start, target)

        if len(path) > 1:
            s.target_cell = path[1]
        else:
            s.target_cell = None

    def move_to_target_cell(s, scene):
        if s.target_cell is None:
            return

        target_x, target_y = s.cell_to_pixel(
            scene,
            s.target_cell[0],
            s.target_cell[1],
            s.size,
        )

        if s.rect.x < target_x:
            s.set_direction("right")
            s.rect.x = min(target_x, s.rect.x + s.speed)
        elif s.rect.x > target_x:
            s.set_direction("left")
            s.rect.x = max(target_x, s.rect.x - s.speed)
        elif s.rect.y < target_y:
            s.set_direction("down")
            s.rect.y = min(target_y, s.rect.y + s.speed)
        elif s.rect.y > target_y:
            s.set_direction("up")
            s.rect.y = max(target_y, s.rect.y - s.speed)

        if s.rect.topleft == (target_x, target_y):
            s.cell_x, s.cell_y = s.target_cell
            s.target_cell = None

    def reset_position(s):
        s.rect.topleft = (s.spawn_x, s.spawn_y)
        s.cell_x = s.spawn_cell_x
        s.cell_y = s.spawn_cell_y
        s.target_cell = None


class PinkGhost(RedGhost):
    DIRECTION_OFFSET = {
        1: (0, -1),
        2: (1, 0),
        4: (0, 1),
        8: (-1, 0),
    }

    def __init__(s, x, y, size, direction, build, cell_size, cell_x, cell_y):
        Ghost.__init__(s, x, y, "pink", size, direction, build)
        s.cell_size = cell_size
        s.spawn_x = x
        s.spawn_y = y
        s.spawn_cell_x = cell_x
        s.spawn_cell_y = cell_y
        s.cell_x = cell_x
        s.cell_y = cell_y
        s.target_cell = None
        s.speed = 5

    def choose_target_cell(s, scene):
        start = (s.cell_x, s.cell_y)
        player_cell = s.pixel_to_cell(scene, scene.player.rect.center)
        direction = scene.player_direction or scene.player.direction
        dx, dy = s.DIRECTION_OFFSET.get(direction, (1, 0))
        target = player_cell
        for _ in range(4):
            next_cell = (target[0] + dx, target[1] + dy)
            neighbors = s.get_neighbors(scene.maze, target[0], target[1])
            if next_cell not in neighbors:
                break
            target = next_cell
        path = s.find_path(scene.maze, start, target)

        if len(path) <= 1:
            path = s.find_path(scene.maze, start, player_cell)

        if len(path) > 1:
            s.target_cell = path[1]
        else:
            s.target_cell = None
