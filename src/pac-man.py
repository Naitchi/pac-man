import sys

from src.config.parser import parse_config
from src.highscore.parser import parse_highscores

# from src.display import Display

# from src.highscore.parser import create_empty_highscores, add_entry
# from src.highscore.models import Highscore


def main(filename: str) -> None:
    try:
        cfg = parse_config(filename)
    except Exception as e:
        print(f"Error parsing config: {e}")
        return

    print(cfg)

    try:
        highscores = parse_highscores(cfg.highscore_filename)
    except Exception as e:
        print(f"Error parsing highscores: {e}")
        return

    print(highscores)

    # create_empty_highscores("test.json")
    # add_entry("test.json", Highscore(name="gcs", score=42))

    # display = Display()
    # display.run()


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".json"):
        print("Usage: make run <config_file.json>")
        sys.exit(1)

    main(sys.argv[1])
