from pydantic import BaseModel, ConfigDict, Field


class LevelConfig(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    width: int = Field(default=10, ge=10, le=25, strict=True)
    height: int = Field(default=10, ge=10, le=25, strict=True)


def default_levels() -> list[LevelConfig]:
    return [
        LevelConfig(width=10, height=10),
        LevelConfig(width=15, height=15),
        LevelConfig(width=20, height=20),
    ]


class GameConfig(BaseModel):
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
