from pydantic import BaseModel


class TeamStanding(BaseModel):
    TeamID: int
    TeamCity: str
    TeamName: str
    Conference: str
    WINS: int
    LOSSES: int
    PlayoffRank: int

class PlayerSeasonStats(BaseModel):
    PLAYER_ID: int
    SEASON_ID: str
    TEAM_ID: int
    TEAM_ABBREVIATION: str
    PLAYER_AGE: int
    GP: int
    MIN: float
    PTS: float
    AST: float
    REB: float
    BLK: float

class TeamSeasonStats(BaseModel):
    TEAM_ID: int
    TEAM_CITY: str
    TEAM_NAME: str
    YEAR: str
    WINS: int
    LOSSES: int
    CONF_RANK: int
    DIV_RANK: int

class TeamScore(BaseModel):
    id: int
    name: str
    score: int | None

class GameInfo(BaseModel):
    game_id: str
    status: str
    home_team: TeamScore
    away_team: TeamScore