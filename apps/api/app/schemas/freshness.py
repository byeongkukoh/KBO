from pydantic import BaseModel


class FreshnessResponse(BaseModel):
    latest_game_date: str | None
    last_successful_sync_at: str | None
    context_updated_at: str | None = None
