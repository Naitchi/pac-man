import sys

from src.config.parser import parse_config
from src.highscore.parser import parse_highscores

from src.game import Game


def main(filename: str) -> None:
    try:
        cfg = parse_config(filename)
    except Exception as e:
        print(f"Error parsing config: {e}")
        return
    try:
        highscores = parse_highscores(cfg.highscore_filename)  # noqa : F841
    except Exception as e:
        print(f"Error parsing highscores: {e}")
        return

    game = Game(cfg)
    game.run()


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".json"):
        print("Usage: make run <config_file.json>")
        sys.exit(1)

    main(sys.argv[1])
