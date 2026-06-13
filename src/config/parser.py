"""Load and validate JSON game configuration files."""

import json
import sys
from typing import Any
from pydantic import ValidationError

from .models import GameConfig


def remove_comments(f: str) -> str:
    """Remove full-line hash comments from JSON content.

    Args:
        f: Raw configuration file content.

    Returns:
        Configuration content without lines beginning with ``#``.
    """
    lines = f.splitlines()
    result: list[str] = []

    for line in lines:
        if not line.strip().startswith("#"):
            result.append(line)

    return "\n".join(result)


def warn_missing_values(data: dict[str, Any]) -> None:
    """Report missing configuration fields that will use defaults.

    Args:
        data: Parsed configuration dictionary.
    """
    missing = sorted(set(GameConfig.model_fields) - set(data) - {"build"})
    if missing:
        print(
            f"Warning: missing config keys: {', '.join(missing)}; "
            "using defaults.",
            file=sys.stderr,
        )

    levels = data.get("levels")
    if not isinstance(levels, list):
        return
    for index, level in enumerate(levels):
        if not isinstance(level, dict):
            continue
        missing = sorted({"width", "height"} - set(level))
        if missing:
            print(
                f"Warning: level {index + 1} is missing "
                f"{', '.join(missing)}; using defaults.",
                file=sys.stderr,
            )


def parse_config(filename: str) -> GameConfig:
    """Read a configuration file and apply validated defaults.

    Invalid JSON or invalid individual values are replaced with safe
    defaults. File access errors are left to the caller so the command-line
    entry point can report a startup failure.

    Args:
        filename: Path to the JSON configuration file.

    Returns:
        A validated game configuration.

    Raises:
        OSError: If the configuration file cannot be opened.
        UnicodeError: If the file cannot be decoded.
    """
    with open(filename, "r") as f:
        content = remove_comments(f.read())

    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        print(
            f"Warning: invalid JSON config ({error}); "
            "using all default values.",
            file=sys.stderr,
        )
        return GameConfig()

    if not isinstance(data, dict):
        print(
            "Warning: invalid config; using all default values.",
            file=sys.stderr,
        )
        return GameConfig()

    warn_missing_values(data)
    config = GameConfig()
    for key, value in data.items():
        if key not in GameConfig.model_fields:
            continue
        try:
            setattr(config, key, value)
        except ValidationError:
            print(
                f"Warning: config key '{key}' is invalid; using default.",
                file=sys.stderr,
            )

    return config
