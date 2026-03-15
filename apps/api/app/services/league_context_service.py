from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import AdvancedMetricConstant, Game, LeagueSeasonBattingContext, LeagueSeasonPitchingContext, PlayerGameBattingStat, PlayerGamePitchingStat, TeamGameStat
from app.services.derived_stats import BattingTotals, PitchingTotals, derive_batting_metrics, derive_pitching_metrics, derive_fip_metric, derive_woba_metrics


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
        intentional_walks=sum(item.intentional_walks for item in batting_rows),
        hit_by_pitch=sum(item.hit_by_pitch for item in batting_rows),
        sacrifice_flies=sum(item.sacrifice_flies for item in batting_rows),
    )
    batting_metrics = derive_batting_metrics(batting_totals)
    plate_appearances = int(batting_metrics["plate_appearances"] or 0)

    pitching_totals = PitchingTotals(
        innings_outs=sum(item.innings_outs for item in pitching_rows),
        hits_allowed=sum(item.hits_allowed for item in pitching_rows),
        walks_allowed=sum(item.walks_allowed for item in pitching_rows),
        hit_by_pitch_allowed=sum(item.hit_by_pitch_allowed for item in pitching_rows),
        strikeouts=sum(item.strikeouts for item in pitching_rows),
        home_runs_allowed=sum(item.home_runs_allowed for item in pitching_rows),
    )
    pitching_metrics = derive_pitching_metrics(pitching_totals)
    earned_runs = sum(item.earned_runs for item in pitching_rows)
    era = round(earned_runs * 27 / pitching_totals.innings_outs, 3) if pitching_totals.innings_outs > 0 else None
    league_runs = int(session.execute(select(func.coalesce(func.sum(TeamGameStat.runs), 0)).where(TeamGameStat.game_id.in_(games))).scalar_one()) // 2

    weights = {
        "WOBA_U_BB_WEIGHT": 0.69,
        "WOBA_HBP_WEIGHT": 0.72,
        "WOBA_1B_WEIGHT": 0.89,
        "WOBA_2B_WEIGHT": 1.27,
        "WOBA_3B_WEIGHT": 1.62,
        "WOBA_HR_WEIGHT": 2.10,
        "WOBA_SCALE": 1.25,
    }
    woba_metrics = derive_woba_metrics(
        batting_totals,
        unintentional_walk_weight=weights["WOBA_U_BB_WEIGHT"],
        hit_by_pitch_weight=weights["WOBA_HBP_WEIGHT"],
        single_weight=weights["WOBA_1B_WEIGHT"],
        double_weight=weights["WOBA_2B_WEIGHT"],
        triple_weight=weights["WOBA_3B_WEIGHT"],
        home_run_weight=weights["WOBA_HR_WEIGHT"],
        woba_scale=weights["WOBA_SCALE"],
        league_woba=0.0,
        league_runs_per_pa=(league_runs / plate_appearances) if plate_appearances > 0 else 0.0,
    )
    league_woba = float(woba_metrics["woba"] or 0.0)
    league_runs_per_pa = (league_runs / plate_appearances) if plate_appearances > 0 else 0.0
    fip_constant = 0.0
    provisional_fip = derive_fip_metric(pitching_totals, fip_constant=0.0)
    if provisional_fip is not None and era is not None:
        fip_constant = round(era - provisional_fip, 3)

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
            runs_scored=league_runs,
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
            hit_by_pitch_allowed=pitching_totals.hit_by_pitch_allowed,
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
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="WOBA_U_BB_WEIGHT", metric_value=weights["WOBA_U_BB_WEIGHT"]),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="WOBA_HBP_WEIGHT", metric_value=weights["WOBA_HBP_WEIGHT"]),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="WOBA_1B_WEIGHT", metric_value=weights["WOBA_1B_WEIGHT"]),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="WOBA_2B_WEIGHT", metric_value=weights["WOBA_2B_WEIGHT"]),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="WOBA_3B_WEIGHT", metric_value=weights["WOBA_3B_WEIGHT"]),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="WOBA_HR_WEIGHT", metric_value=weights["WOBA_HR_WEIGHT"]),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="WOBA_SCALE", metric_value=weights["WOBA_SCALE"]),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="LEAGUE_WOBA", metric_value=league_woba),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="LEAGUE_R_PER_PA", metric_value=league_runs_per_pa),
            AdvancedMetricConstant(season_id=season, series_code=series_code, metric_code="FIP_CONSTANT", metric_value=fip_constant),
        ]
    )
