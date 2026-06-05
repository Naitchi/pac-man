import pygame
from .base import Scene
from ..entities.player import Player
import random


class MainMenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        # TODO voir pour mettre une font custom en mode pixelise
        self.title_font = pygame.font.Font(None, 72)
        self.info_font = pygame.font.Font(None, 32)
        self.leaderboard_title_font = pygame.font.Font(None, 42)
        self.leaderboard_font = pygame.font.Font(None, 28)
        self.player_x = 0
        self.player_y = random.randint(0, self.game.screen.get_height() - 100)
        self.player = Player(
            self.player_x,
            self.player_y,
            self.game.config.build)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                from .play import PlayScene
                self.game.change_scene(PlayScene(self.game))
            elif event.key == pygame.K_ESCAPE:
                self.game.running = False

    def update(self, dt):
        self.player_x += 16
        self.player.rect.x = self.player_x
        if self.game.screen.get_width() < self.player_x:
            self.player_x = -100
            self.player_y = random.randint(
                0, self.game.screen.get_height() - 100)
            self.player.rect.y = self.player_y
        self.player.update(dt)

    def draw(self, screen):
        screen.fill((10, 10, 40))
        self.player.draw(screen)
        title = self.title_font.render("PAC-MAN", True, (255, 200, 0))
        info1 = self.info_font.render(
            "Press Enter to play", True, (255, 255, 255))
        info2 = self.info_font.render(
            "Press Escape to quit", True, (255, 255, 255))
        screen.blit(
            title,
            title.get_rect(
                center=(
                    screen.get_width() //
                    2,
                    180)))
        screen.blit(
            info1,
            info1.get_rect(
                center=(
                    screen.get_width() //
                    2,
                    260)))
        screen.blit(info2, info2.get_rect(
            center=(screen.get_width() // 2, screen.get_height() - 180)))
        self.draw_leaderboard(screen)

    def draw_leaderboard(self, screen):
        x = 60
        y = 150
        title = self.leaderboard_title_font.render(
            "LEADERBOARD :", True, (255, 200, 0))
        screen.blit(title, (x, y))

        highscores = self.game.highscores.highscores
        if not highscores:
            empty = self.leaderboard_font.render(
                "No scores", True, (255, 255, 255))
            screen.blit(empty, (x, y + 50))
            return

        for index, entry in enumerate(highscores[:10], start=1):
            line = self.leaderboard_font.render(
                f"{index}. {entry.name} - {entry.score}",
                True,
                (255, 255, 255))
            screen.blit(line, (x, y + 35 + index * 28))
