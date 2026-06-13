from pathlib import Path
import sys

from pydantic import ValidationError

from .models import Highscore, HighscoreFile


def sort_highscores(highscores: HighscoreFile) -> HighscoreFile:
    highscores.highscores.sort(key=lambda entry: entry.score, reverse=True)
    return highscores


def create_empty_highscores(filename: str) -> HighscoreFile:
    highscores = HighscoreFile(highscores=[])
    with open(filename, "w") as f:
        f.write(highscores.model_dump_json(indent=4) + "\n")
    return highscores


def read_highscores(filename: str) -> HighscoreFile:
    with open(filename, "r") as f:
        content = f.read()

    if not content.strip():
        return create_empty_highscores(filename)

    return HighscoreFile.model_validate_json(content)


def parse_highscores(filename: str) -> HighscoreFile:
    if not Path(filename).exists():
        print(
            f"Warning: highscore file '{filename}' is missing; "
            "creating an empty file.",
            file=sys.stderr,
        )
        return create_empty_highscores(filename)

    try:
        return sort_highscores(read_highscores(filename))
    except (OSError, UnicodeError, ValidationError) as error:
        print(
            f"Warning: highscore file '{filename}' is invalid "
            f"({error}); creating an empty file.",
            file=sys.stderr,
        )
        return create_empty_highscores(filename)


def write_highscores(filename: str, highscores: HighscoreFile) -> None:
    if not Path(filename).exists():
        raise FileNotFoundError(2, "No such file or directory", filename)

    with open(filename, "w") as f:
        f.write(highscores.model_dump_json(indent=4) + "\n")


def add_entry(filename: str, entry: Highscore,
              build: bool = False) -> HighscoreFile:

    if build:
        filename = "_internal/json/highscores.json"

    highscores = parse_highscores(filename)
    highscores.highscores.append(entry)
    sort_highscores(highscores)
    highscores.highscores = highscores.highscores[:10]
    write_highscores(filename, highscores)
    return highscores
