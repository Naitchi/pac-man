import pygame


class Ghost:
    # le comportement pour les sprites sera le meme pour tous, pour les ia
    # diff on fera du polymorphisme ca sera propre et cool
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

    def update(s):
        s.frame_count += 1

        if s.frame_count >= s.animation_speed:
            s.frame_count = 0
            s.current_frame = (s.current_frame + 1) % len(s.sprites)
            s.image = s.sprites[s.current_frame]

    def draw(self, screen):
        screen.blit(self.image, self.rect)
