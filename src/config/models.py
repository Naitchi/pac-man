"""Validated models for game configuration."""

from pydantic import BaseModel, ConfigDict, Field


class LevelConfig(BaseModel):
    """Describe the dimensions of a generated maze.

    Attributes:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
    """

    model_config = ConfigDict(validate_assignment=True)

    width: int = Field(default=10, ge=10, le=25, strict=True)
    height: int = Field(default=10, ge=10, le=25, strict=True)


def default_levels() -> list[LevelConfig]:
    """Create the default sequence of level configurations.

    Returns:
        Three validated level configurations of increasing size.
    """
    return [
        LevelConfig(width=10, height=10),
        LevelConfig(width=15, height=15),
        LevelConfig(width=20, height=20),
    ]


class GameConfig(BaseModel):
    """Store validated settings used by the game.

    Attributes:
        build: Whether resources are loaded from a packaged build.
        highscore_filename: JSON file used for persistent highscores.
        levels: Maze dimensions cycled through during the game.
        lives: Number of lives available at the start of a game.
        points_per_pacgum: Score awarded for a regular pacgum.
        points_per_super_pacgum: Score awarded for a super-pacgum.
        points_per_ghost: Score awarded for eating a ghost.
        seed: Fixed seed used to generate the first level.
        level_max_time: Time limit for each level in seconds.
    """

    model_config = ConfigDict(validate_assignment=True)

    build: bool = False
    highscore_filename: str = Field(default="highscores.json", min_length=1)
    levels: list[LevelConfig] = Field(
        default_factory=default_levels,
        min_length=1,
    )
    lives: int = Field(default=3, gt=0, strict=True)
    points_per_pacgum: int = Field(default=10, gt=0, strict=True)
    points_per_super_pacgum: int = Field(default=50, gt=0, strict=True)
    points_per_ghost: int = Field(default=200, gt=0, strict=True)
    seed: int = Field(default=42, ge=0, strict=True)
    level_max_time: int = Field(default=90, gt=0, strict=True)
