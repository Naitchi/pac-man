from .models import GameConfig


def remove_comments(f: str) -> str:
    lines = f.splitlines()
    result = []

    for line in lines:
        if not line.strip().startswith("#"):
            result.append(line)

    return "\n".join(result)


def parse_config(filename: str) -> GameConfig:
    with open(filename, "r") as f:
        config = GameConfig.model_validate_json(remove_comments(f.read()))
    return config
