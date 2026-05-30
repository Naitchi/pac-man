import pygame

from .base import Scene
from src.highscore.parser import add_entry
from src.highscore.models import Highscore


class EndScene(Scene):

    def __init__(self, game: object, score: int, won: bool = False) -> None:
        super().__init__(game)
        self.score = score
        self.won = won
        self.username = ""
        self.title_font = pygame.font.Font(None, 72)
        self.info_font = pygame.font.Font(None, 32)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.running = False
            elif event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif len(self.username) < 10 and (event.unicode.isalnum() or
                                              event.unicode == " "):
                self.username += event.unicode
            elif event.key == pygame.K_RETURN:
                if self.username:
                    highscore = Highscore(name=self.username, score=self.score)
                    add_entry(self.game.config.highscore_filename, highscore)
                    self.game.running = False

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((10, 10, 40))

        title_text = "VICTORY" if self.won else "GAME OVER"
        title_color = (80, 255, 120) if self.won else (255, 80, 80)
        title = self.title_font.render(title_text, True, title_color)
        score = self.info_font.render(
            f"Final score: {self.score}", True, (255, 255, 255)
        )
        name = self.info_font.render(
            f"Enter name: {self.username}", True, (255, 255, 255)
        )
        quit_info = self.info_font.render(
            "Press Escape to quit", True, (180, 180, 180)
        )

        center_x = screen.get_width() // 2
        screen.blit(title, title.get_rect(center=(center_x, 180)))
        screen.blit(score, score.get_rect(center=(center_x, 260)))
        screen.blit(name, name.get_rect(center=(center_x, 340)))
        screen.blit(
            quit_info,
            quit_info.get_rect(center=(center_x, screen.get_height() - 180)),
        )
