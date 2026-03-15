from pydantic import BaseModel

from app.schemas.freshness import FreshnessResponse


class GameListItemResponse(BaseModel):
    game_id: str
    game_date: str
    series_code: str
    series_name: str
    stadium: str
    away_team_code: str
    home_team_code: str
    away_score: int
    home_score: int
    status_code: str


class GameListResponse(BaseModel):
    season: int
    series_code: str | None
    team_code: str | None
    game_date: str | None
    page: int
    page_size: int
    total_count: int
    total_pages: int
    freshness: FreshnessResponse
    items: list[GameListItemResponse]
