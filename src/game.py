import pygame
from src.config.models import GameConfig
from src.scenes.end_scene import EndScene


class Game:
    def __init__(self, config: GameConfig):
        pygame.init()
        self.config = config
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.running = True

        # temp pour tester l'écran de fin
        self.scene = EndScene(self, 4242, True)

    def change_scene(self, new_scene):
        if hasattr(self, "scene") and self.scene:
            try:
                self.scene.on_exit()
            except Exception:
                pass
        self.scene = new_scene
        try:
            self.scene.on_enter()
        except Exception:
            pass

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
