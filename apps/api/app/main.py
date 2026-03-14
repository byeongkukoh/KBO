from fastapi import FastAPI

from app.api.routes.games import router as games_router
from app.api.routes.health import router as health_router
from app.api.routes.players import router as players_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="KBO Record API",
        description="KBO 선수 및 팀 기록 서비스를 위한 FastAPI 백엔드",
        version="0.1.0",
    )
    app.include_router(health_router, prefix="/api")
    app.include_router(games_router, prefix="/api")
    app.include_router(players_router, prefix="/api")
    return app


app = create_app()
