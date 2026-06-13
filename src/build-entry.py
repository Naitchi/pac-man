"""PyInstaller entry point for the packaged game."""

from pathlib import Path
import sys
import os

from src.highscore.parser import parse_highscores
from src.config.parser import parse_config
from src.game import Game


def main() -> None:
    """Load packaged resources and start the game."""
    try:
        os.chdir(Path(sys.executable).parent)
    except OSError as e:
        print(f"Error opening game directory: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        cfg = parse_config("_internal/json/config.json")
    except Exception as e:
        print(f"Error parsing config: {e}", file=sys.stderr)
        sys.exit(1)

    cfg.build = True

    try:
        highscores = parse_highscores("_internal/json/highscores.json")
    except Exception as e:
        print(f"Error parsing highscores: {e}", file=sys.stderr)
        sys.exit(1)

    game = Game(cfg, highscores)
    game.run()


if __name__ == "__main__":
    main()
