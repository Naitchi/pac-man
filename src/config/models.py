from pydantic import BaseModel, ConfigDict, Field


class LevelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    width: int = Field(gt=0)
    height: int = Field(gt=0)


class GameConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    highscore_filename: str = Field(min_length=1)
    levels: list[LevelConfig] = Field(min_length=1)
    lives: int = Field(gt=0)
    pacgum: int = Field(gt=0)
    points_per_pacgum: int = Field(gt=0)
    points_per_super_pacgum: int = Field(gt=0)
    points_per_ghost: int = Field(gt=0)
    seed: int = Field(ge=0)
    level_max_time: int = Field(gt=0)
