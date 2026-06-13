"""Main menu scene and highscore display."""

from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
import random

from ..entities.player import Player
from .base import Scene

if TYPE_CHECKING:
    from src.game import Game


class MainMenuScene(Scene):
    """Display the title screen, controls, and current leaderboard."""

    def __init__(self, game: Game) -> None:
        """Initialize menu fonts and the decorative Pac-Man sprite.

        Args:
            game: Active game controller.
        """
        super().__init__(game)
        self.title_font: pygame.font.Font = pygame.font.Font(None, 72)
        self.info_font: pygame.font.Font = pygame.font.Font(None, 32)
        self.leaderboard_title_font: pygame.font.Font = pygame.font.Font(
            None, 42
        )
        self.leaderboard_font: pygame.font.Font = pygame.font.Font(None, 28)
        self.player_x: int = 0
        self.player_y: int = random.randint(
            0, self.game.screen.get_height() - 100
        )
        self.player: Player = Player(
            self.player_x, self.player_y, self.game.config.build
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Start the game or close the application.

        Args:
            event: Event received from the Pygame event queue.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                from .play import PlayScene

                self.game.change_scene(PlayScene(self.game))
            elif event.key == pygame.K_ESCAPE:
                self.game.running = False

    def update(self, dt: float) -> None:
        """Animate the decorative Pac-Man across the menu.

        Args:
            dt: Elapsed time since the previous frame in seconds.
        """
        self.player_x += 16
        self.player.rect.x = self.player_x
        if self.game.screen.get_width() < self.player_x:
            self.player_x = -100
            self.player_y = random.randint(
                0, self.game.screen.get_height() - 100
            )
            self.player.rect.y = self.player_y
        self.player.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Render the menu and leaderboard.

        Args:
            screen: Destination display surface.
        """
        screen.fill((10, 10, 40))
        self.player.draw(screen)
        title = self.title_font.render("PAC-MAN", True, (255, 200, 0))
        info1 = self.info_font.render(
            "Press Enter to play", True, (255, 255, 255)
        )
        info2 = self.info_font.render(
            "Press Escape to quit", True, (255, 255, 255)
        )

        guide = self.info_font.render(
            "Use arrow keys to move, collect all pellets to win! don't "
            "get caught by the ghosts!",
            True,
            (255,
             255,
             255))
        screen.blit(
            title, title.get_rect(center=(screen.get_width() // 2, 180))
        )
        screen.blit(
            info1, info1.get_rect(center=(screen.get_width() // 2, 260))
        )
        screen.blit(
            info2,
            info2.get_rect(
                center=(screen.get_width() // 2, screen.get_height() - 180)
            ),
        )
        screen.blit(
            guide,
            guide.get_rect(
                center=(
                    screen.get_width() //
                    2,
                    screen.get_height() -
                    100)))
        self.draw_leaderboard(screen)

    def draw_leaderboard(self, screen: pygame.Surface) -> None:
        """Render up to ten highscores.

        Args:
            screen: Destination display surface.
        """
        x = 60
        y = 150
        title = self.leaderboard_title_font.render(
            "LEADERBOARD :", True, (255, 200, 0)
        )
        screen.blit(title, (x, y))

        highscores = self.game.highscores.highscores
        if not highscores:
            empty = self.leaderboard_font.render(
                "No scores", True, (255, 255, 255)
            )
            screen.blit(empty, (x, y + 50))
            return

        for index, entry in enumerate(highscores[:10], start=1):
            line = self.leaderboard_font.render(
                f"{index}. {entry.name} - {entry.score}", True, (255, 255, 255)
            )
            screen.blit(line, (x, y + 35 + index * 28))
