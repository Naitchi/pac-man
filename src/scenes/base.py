"""Base interface shared by all game scenes."""

from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.game import Game


class Scene:
    """Define the lifecycle and frame interface for a game scene."""

    def __init__(self, game: Game) -> None:
        """Store the game controller used by the scene.

        Args:
            game: Active game controller.
        """
        self.game: Game = game

    def on_enter(self) -> None:
        """Run optional setup when the scene becomes active."""
        pass

    def on_exit(self) -> None:
        """Run optional cleanup before the scene is replaced."""
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one Pygame event.

        Args:
            event: Event received from the Pygame event queue.
        """
        pass

    def update(self, dt: float) -> None:
        """Advance scene state by one frame.

        Args:
            dt: Elapsed time since the previous frame in seconds.
        """
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Render the scene on the application surface.

        Args:
            screen: Destination display surface.
        """
        pass
