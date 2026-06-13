"""Command-line entry point for the Pac-Man game."""

import sys

from src.highscore.parser import parse_highscores
from src.config.parser import parse_config
from src.game import Game


def main(filename: str) -> None:
    """Load the configuration and start the game.

    Args:
        filename: Path to the JSON configuration file.
    """
    try:
        cfg = parse_config(filename)
    except Exception as e:
        print(f"Error parsing config: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        highscores = parse_highscores(cfg.highscore_filename)
    except Exception as e:
        print(f"Error parsing highscores: {e}", file=sys.stderr)
        sys.exit(1)

    game = Game(cfg, highscores)
    game.run()


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".json"):
        print("Usage: python3 pac-man.py <config_file.json>", file=sys.stderr)
        sys.exit(1)

    main(sys.argv[1])
