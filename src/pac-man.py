import sys

from src.config.parser import parse_config
from src.highscore.parser import parse_highscores

from src.game import Game

# from src.highscore.parser import create_empty_highscores, add_entry
# from src.highscore.models import Highscore


def main(filename: str) -> None:
    try:
        cfg = parse_config(filename)
    except Exception as e:
        print(f"Error parsing config: {e}")
        return
    try:
        highscores = parse_highscores(cfg.highscore_filename)
    except Exception as e:
        print(f"Error parsing highscores: {e}")
        return
    # create_empty_highscores("test.json")
    # add_entry("test.json", Highscore(name="gcs", score=42))

    game = Game()
    game.run()


if __name__ == "__main__":
    file = ""
    if len(sys.argv) == 1:
        file = "config.json"
    elif len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        file = sys.argv[1]
    else:
        print("Usage: make run <config_file.json>")
        sys.exit(1)

    main(file)
