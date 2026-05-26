from mazegenerator import MazeGenerator
import pygame


class Display():
    DARK_BLUE = (10, 10, 40)

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.running = True
        self.maze = MazeGenerator((20, 20), perfect=False, seed=42).maze

    def run(self) -> None:
        print(self.maze)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            self.screen.fill(Display.DARK_BLUE)

            pygame.display.flip()

            self.clock.tick(60)
