import json
import sys
from typing import Any
from pydantic import ValidationError

from .models import GameConfig


def remove_comments(f: str) -> str:
    lines = f.splitlines()
    result = []

    for line in lines:
        if not line.strip().startswith("#"):
            result.append(line)

    return "\n".join(result)


def warn_missing_values(data: dict[str, Any]) -> None:
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
