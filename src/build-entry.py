import os
import sys
from pathlib import Path

from src.config.parser import parse_config
from src.game import Game
from src.highscore.parser import parse_highscores


def main() -> None:
    try:
        os.chdir(Path(sys.executable).parent)
    except OSError as e:
        print(f"Error opening game directory: {e}")
        return

    try:
        cfg = parse_config("_internal/json/config.json")
    except Exception as e:
        print(f"Error parsing config: {e}")
        return

    try:
        highscores = parse_highscores("_internal/json/highscores.json")  # noqa : F841
    except Exception as e:
        print(f"Error parsing highscores: {e}")
        return

    game = Game(cfg)
    game.run()


if __name__ == "__main__":
    main()
