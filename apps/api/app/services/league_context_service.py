from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import AdvancedMetricConstant, Game, LeagueSeasonBattingContext, LeagueSeasonPitchingContext, PlayerGameBattingStat, PlayerGamePitchingStat
from app.services.derived_stats import BattingTotals, PitchingTotals, derive_batting_metrics, derive_pitching_metrics


def refresh_league_context(session: Session, season: int, series_code: str) -> None:
    games = list(session.execute(select(Game.id).where(Game.season_id == season, Game.series_code == series_code)).scalars())
    if not games:
        return

    batting_rows = list(session.execute(select(PlayerGameBattingStat).where(PlayerGameBattingStat.game_id.in_(games))).scalars())
    pitching_rows = list(session.execute(select(PlayerGamePitchingStat).where(PlayerGamePitchingStat.game_id.in_(games))).scalars())

    batting_totals = BattingTotals(
        at_bats=sum(item.at_bats for item in batting_rows),
        hits=sum(item.hits for item in batting_rows),
        doubles=sum(item.doubles for item in batting_rows),
        triples=sum(item.triples for item in batting_rows),
        home_runs=sum(item.home_runs for item in batting_rows),
        strikeouts=sum(item.strikeouts for item in batting_rows),
        walks=sum(item.walks for item in batting_rows),
        hit_by_pitch=sum(item.hit_by_pitch for item in batting_rows),
        sacrifice_flies=sum(item.sacrifice_flies for item in batting_rows),
    )
    batting_metrics = derive_batting_metrics(batting_totals)
    plate_appearances = int(batting_metrics["plate_appearances"] or 0)

    pitching_totals = PitchingTotals(
        innings_outs=sum(item.innings_outs for item in pitching_rows),
        hits_allowed=sum(item.hits_allowed for item in pitching_rows),
        walks_allowed=sum(item.walks_allowed for item in pitching_rows),
        strikeouts=sum(item.strikeouts for item in pitching_rows),
    )
    pitching_metrics = derive_pitching_metrics(pitching_totals)
    earned_runs = sum(item.earned_runs for item in pitching_rows)
    era = round(earned_runs * 27 / pitching_totals.innings_outs, 3) if pitching_totals.innings_outs > 0 else None

    session.execute(delete(LeagueSeasonBattingContext).where(LeagueSeasonBattingContext.season_id == season, LeagueSeasonBattingContext.series_code == series_code))
    session.execute(delete(LeagueSeasonPitchingContext).where(LeagueSeasonPitchingContext.season_id == season, LeagueSeasonPitchingContext.series_code == series_code))
    session.execute(delete(AdvancedMetricConstant).where(AdvancedMetricConstant.season_id == season, AdvancedMetricConstant.series_code == series_code))

    session.add(
        LeagueSeasonBattingContext(
            season_id=season,
            series_code=series_code,
            plate_appearances=plate_appearances,
            at_bats=batting_totals.at_bats,
            hits=batting_totals.hits,
            doubles=batting_totals.doubles,
            triples=batting_totals.triples,
            home_runs=batting_totals.home_runs,
            stolen_bases=sum(item.stolen_bases for item in batting_rows),
            strikeouts=batting_totals.strikeouts,
            walks=batting_totals.walks,
            hit_by_pitch=batting_totals.hit_by_pitch,
            sacrifice_flies=batting_totals.sacrifice_flies,
            batting_avg=float(batting_metrics["avg"]) if batting_metrics["avg"] is not None else None,
            obp=float(batting_metrics["obp"]) if batting_metrics["obp"] is not None else None,
            slg=float(batting_metrics["slg"]) if batting_metrics["slg"] is not None else None,
            ops=float(batting_metrics["ops"]) if batting_metrics["ops"] is not None else None,
        )
    )
    session.add(
        LeagueSeasonPitchingContext(
            season_id=season,
            series_code=series_code,
            innings_outs=pitching_totals.innings_outs,
            hits_allowed=pitching_totals.hits_allowed,
            walks_allowed=pitching_totals.walks_allowed,
            strikeouts=pitching_totals.strikeouts,
            earned_runs=earned_runs,
            era=era,
            whip=float(pitching_metrics["whip"]) if pitching_metrics["whip"] is not None else None,
        )
    )
    session.add_all(
        [
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="OPS_PLUS_BASELINE", metric_value=100.0),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="ERA_PLUS_BASELINE", metric_value=100.0),
        ]
    )
