import pygame
from .base import Scene


class MainMenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        # TODO voir pour mettre une font custom en mode pixelise
        self.title_font = pygame.font.Font(None, 72)
        self.info_font = pygame.font.Font(None, 32)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                from .play import PlayScene
                self.game.change_scene(PlayScene(self.game))
            elif event.key == pygame.K_ESCAPE:
                self.game.running = False

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((10, 10, 40))
        title = self.title_font.render("PAC-MAN", True, (255, 200, 0))
        info1 = self.info_font.render(
            "Press Enter to play", True, (255, 255, 255))
        info2 = self.info_font.render(
            "Press Escape to quit", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, 180)))
        screen.blit(info1, info1.get_rect(center=(screen.get_width()//2, 260)))
        screen.blit(info2, info2.get_rect(
            center=(screen.get_width()//2, screen.get_height() - 180)))
