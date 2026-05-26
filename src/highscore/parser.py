from pathlib import Path

from .models import Highscore, HighscoreFile


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
        return create_empty_highscores(filename)

    return read_highscores(filename)


def write_highscores(filename: str, highscores: HighscoreFile) -> None:
    if not Path(filename).exists():
        raise FileNotFoundError(2, "No such file or directory", filename)

    with open(filename, "w") as f:
        f.write(highscores.model_dump_json(indent=4) + "\n")


def add_entry(filename: str, entry: Highscore) -> HighscoreFile:
    if not Path(filename).exists():
        raise FileNotFoundError(2, "No such file or directory", filename)

    highscores = read_highscores(filename)
    highscores.highscores.append(entry)
    highscores.highscores.sort(key=lambda entry: entry.score, reverse=True)
    highscores.highscores = highscores.highscores[:10]
    write_highscores(filename, highscores)
    return highscores
