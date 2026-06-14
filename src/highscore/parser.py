"""Read, validate, sort, and persist highscores."""

from pathlib import Path
import sys

from pydantic import ValidationError

from .models import Highscore, HighscoreFile


def sort_highscores(highscores: HighscoreFile) -> HighscoreFile:
    """Sort highscore entries in descending score order.

    Args:
        highscores: Validated highscore collection to sort.

    Returns:
        The same collection with entries sorted in place.
    """
    highscores.highscores.sort(key=lambda entry: entry.score, reverse=True)
    return highscores


def create_empty_highscores(filename: str) -> HighscoreFile:
    """Create an empty highscore file.

    Args:
        filename: Destination JSON filename.

    Returns:
        The empty validated highscore collection.

    Raises:
        OSError: If the file cannot be created or written.
    """
    highscores = HighscoreFile(highscores=[])
    with open(filename, "w") as f:
        f.write(highscores.model_dump_json(indent=4) + "\n")
    return highscores


def read_highscores(filename: str) -> HighscoreFile:
    """Read and validate a highscore file.

    Args:
        filename: Path to the highscore JSON file.

    Returns:
        The validated highscore collection.

    Raises:
        OSError: If the file cannot be read.
        ValidationError: If the JSON structure or entries are invalid.
    """
    with open(filename, "r") as f:
        content = f.read()

    if not content.strip():
        return create_empty_highscores(filename)

    return HighscoreFile.model_validate_json(content)


def parse_highscores(filename: str) -> HighscoreFile:
    """Load highscores and recover from missing or invalid content.

    Args:
        filename: Path to the highscore JSON file.

    Returns:
        A sorted collection, or an empty collection after recovery.

    Raises:
        OSError: If an empty replacement file cannot be created.
    """
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
    """Write validated highscores to an existing file.

    Args:
        filename: Destination JSON filename.
        highscores: Validated collection to serialize.

    Raises:
        FileNotFoundError: If the destination file does not exist.
        OSError: If the destination cannot be written.
    """
    if not Path(filename).exists():
        raise FileNotFoundError(2, "No such file or directory", filename)

    with open(filename, "w") as f:
        f.write(highscores.model_dump_json(indent=4) + "\n")


def add_entry(filename: str, entry: Highscore,
              build: bool = False) -> HighscoreFile:
    """Insert a score and persist the ten highest entries.

    Args:
        filename: Highscore JSON filename used in development mode.
        entry: Validated score to add.
        build: Whether to use the packaged highscore path.

    Returns:
        The updated, sorted top-ten collection.

    Raises:
        OSError: If the highscore file cannot be created or written.
    """
    if build:
        filename = "_internal/json/highscores.json"

    highscores = parse_highscores(filename)
    highscores.highscores.append(entry)
    sort_highscores(highscores)
    highscores.highscores = highscores.highscores[:10]
    write_highscores(filename, highscores)
    return highscores
