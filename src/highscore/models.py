"""Validated models for persistent highscores."""

from pydantic import BaseModel, ConfigDict, Field


class Highscore(BaseModel):
    """Represent one validated highscore entry.

    Attributes:
        name: Player name containing up to ten ASCII letters, digits, or
            spaces.
        score: Non-negative score achieved by the player.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=10, pattern=r"^[A-Za-z0-9 ]+$")
    score: int = Field(ge=0, strict=True)


class HighscoreFile(BaseModel):
    """Represent the validated content of the highscore JSON file.

    Attributes:
        highscores: Collection containing at most ten score entries.
    """

    model_config = ConfigDict(extra="forbid")

    highscores: list[Highscore] = Field(max_length=10)
