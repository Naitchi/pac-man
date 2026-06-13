"""Application controller and main Pygame loop."""

import pygame
from src.highscore.models import HighscoreFile
from src.scenes.menu import MainMenuScene
from src.config.models import GameConfig
from src.scenes.base import Scene


class Game:
    """Coordinate configuration, scenes, rendering, and application state."""

    def __init__(self, config: GameConfig, highscores: HighscoreFile) -> None:
        """Initialize Pygame and create the main menu.

        Args:
            config: Validated game configuration.
            highscores: Highscores loaded at application startup.
        """
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
        """Replace the active scene and invoke lifecycle hooks.

        Args:
            new_scene: Scene that should receive subsequent events and frames.
        """
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
        """Run the main event, update, and rendering loop."""
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
