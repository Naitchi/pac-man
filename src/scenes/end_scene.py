"""Victory and game-over scene with highscore entry."""

import sys

import pygame
from src.highscore.parser import add_entry
from src.highscore.models import Highscore
from src.scenes.menu import MainMenuScene
from src.entities.ghost import Ghost
from src.game import Game
from .base import Scene


def is_valid_username_character(character: str) -> bool:
    """Check whether a character is valid in a player name.

    Args:
        character: Character entered through a keyboard event.

    Returns:
        ``True`` for one ASCII letter, digit, or space.
    """
    return (
        len(character) == 1
        and character.isascii()
        and (character.isalnum() or character == " ")
    )


class EndScene(Scene):
    """Display the final result and collect the player's name."""

    def __init__(self, game: Game, score: int, won: bool = False) -> None:
        """Initialize the final score screen.

        Args:
            game: Active game controller.
            score: Final score achieved by the player.
            won: Whether the player completed every level.
        """
        super().__init__(game)
        self.score: int = score
        self.won: bool = won
        self.username: str = ""
        self.show_info: str = f"Enter name: {self.username}"
        self.show_info_status: int = 1
        self.title_font: pygame.font.Font = pygame.font.Font(None, 72)
        self.info_font: pygame.font.Font = pygame.font.Font(None, 32)

        self.left_ghost: Ghost = Ghost(
            0,
            0,
            "red",
            72,
            "down",
            self.game.config.build,
        )
        self.right_ghost: Ghost = Ghost(
            0,
            0,
            "blue",
            72,
            "down",
            self.game.config.build,
        )
        if self.won:
            self.left_ghost.set_modifier("white")
            self.right_ghost.set_modifier("scared")

    def handle_event(self, event: pygame.event.Event) -> None:
        """Process name entry, score saving, and exit actions.

        Args:
            event: Event received from the Pygame event queue.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif (
                event.key == pygame.K_BACKSPACE
                and self.show_info_status == 1
            ):
                self.username = self.username[:-1]
                self.show_info = f"Enter name: {self.username}"
            elif (
                self.show_info_status == 1
                and len(self.username) < 10
                and is_valid_username_character(event.unicode)
            ):
                self.username += event.unicode
                self.show_info = f"Enter name: {self.username}"
            elif event.key == pygame.K_RETURN:
                if self.username and self.show_info_status == 1:
                    try:
                        highscore = Highscore(
                            name=self.username, score=self.score)
                        self.game.highscores = add_entry(
                            self.game.config.highscore_filename, highscore,
                            self.game.config.build)
                        self.show_info_status = 0
                        self.show_info = "Score saved! Press Return to restart"
                    except Exception as e:
                        print(f"Error saving score: {e}", file=sys.stderr)

                elif self.show_info_status == 0:
                    self.game.change_scene(MainMenuScene(self.game))

    def update(self, dt: float) -> None:
        """Advance decorative ghost animations.

        Args:
            dt: Elapsed time since the previous frame in seconds.
        """
        self.left_ghost.update_animation()
        self.right_ghost.update_animation()

    def draw(self, screen: pygame.Surface) -> None:
        """Render the result, score, and name prompt.

        Args:
            screen: Destination display surface.
        """
        screen.fill((10, 10, 40))

        title_text = "VICTORY" if self.won else "GAME OVER"
        title_color = (80, 255, 120) if self.won else (255, 80, 80)
        title = self.title_font.render(title_text, True, title_color)
        score = self.info_font.render(
            f"Final score: {self.score}", True, (255, 255, 255)
        )
        name = self.info_font.render(self.show_info, True, (255, 255, 255))
        quit_info = self.info_font.render(
            "Press Escape to quit", True, (180, 180, 180)
        )

        center_x = screen.get_width() // 2
        title_rect = title.get_rect(center=(center_x, 180))

        self.left_ghost.rect.center = (
            title_rect.left - 60,
            title_rect.centery,
        )
        self.right_ghost.rect.center = (
            title_rect.right + 60,
            title_rect.centery,
        )

        self.left_ghost.draw(screen)
        self.right_ghost.draw(screen)

        if self.won:
            congrats_text = self.info_font.render(
                "Congratulations! You won!", True, (255, 255, 255)
            )
            screen.blit(
                congrats_text,
                congrats_text.get_rect(
                    center=(
                        center_x,
                        260)))

        screen.blit(title, title_rect)
        screen.blit(score, score.get_rect(center=(center_x, 340)))
        screen.blit(name, name.get_rect(center=(center_x, 420)))
        screen.blit(
            quit_info,
            quit_info.get_rect(center=(center_x, screen.get_height() - 180)),
        )
