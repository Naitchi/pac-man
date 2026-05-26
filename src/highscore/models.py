from pydantic import BaseModel, ConfigDict, Field


class Highscore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=10, pattern=r"^[A-Za-z0-9 ]+$")
    score: int = Field(ge=0)


class HighscoreFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    highscores: list[Highscore] = Field(max_length=10)
