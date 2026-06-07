import pygame  # pyright: ignore[reportMissingImports]

from src.highscore.models import HighscoreFile
from src.scenes.menu import MainMenuScene
from src.config.models import GameConfig
from src.scenes.base import Scene


class Game:
    def __init__(self, config: GameConfig, highscores: HighscoreFile) -> None:
        pygame.init()
        self.config: GameConfig = config
        self.highscores: HighscoreFile = highscores
        self.screen: pygame.Surface = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN
        )
        pygame.display.set_caption("Pac-Man")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        self.scene: Scene = MainMenuScene(self)

    def change_scene(self, new_scene: Scene) -> None:
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

    def run(self) -> None:
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
