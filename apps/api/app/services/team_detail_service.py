from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Game, LeagueSeasonBattingContext, LeagueSeasonPitchingContext, Team, TeamGameStat
from app.services.derived_stats import BattingTotals, safe_ratio
from app.services.season_center.standings import format_streak
from app.services.season_center.types import TeamAccumulator


def get_team_season_detail(session: Session, season: int, team_code: str, series_code: str | None) -> dict[str, object] | None:
    team = session.execute(select(Team).where(Team.team_code == team_code)).scalar_one_or_none()
    if team is None:
        return None
    stmt: Select[tuple[Game]] = (
        select(Game)
        .where(Game.season_id == season, or_(Game.away_team_id == team.id, Game.home_team_id == team.id))
        .options(
            selectinload(Game.away_team),
            selectinload(Game.home_team),
            selectinload(Game.team_game_stats).selectinload(TeamGameStat.team),
            selectinload(Game.player_batting_stats),
            selectinload(Game.player_pitching_stats),
        )
        .order_by(Game.game_date.desc(), Game.kbo_game_id.desc())
    )
    if series_code is not None:
        stmt = stmt.where(Game.series_code == series_code)
    games = list(session.execute(stmt).scalars())
    if not games:
        return None

    accumulator = TeamAccumulator(team_code=team.team_code, team_name=team.team_name)
    recent_games: list[dict[str, object]] = []
    for game in games:
        is_home = game.home_team_id == team.id
        runs_for = game.home_score if is_home else game.away_score
        runs_against = game.away_score if is_home else game.home_score
        accumulator.games += 1
        accumulator.runs_scored += runs_for
        accumulator.runs_allowed += runs_against
        if runs_for > runs_against:
            accumulator.wins += 1
            accumulator.recent_results.append("W")
        elif runs_for < runs_against:
            accumulator.losses += 1
            accumulator.recent_results.append("L")
        else:
            accumulator.draws += 1
            accumulator.recent_results.append("D")
        team_stats = next((item for item in game.team_game_stats if item.team_id == team.id), None)
        if team_stats is not None:
            accumulator.hits += team_stats.hits
        batting_rows = [row for row in game.player_batting_stats if row.team_id == team.id]
        pitching_rows = [row for row in game.player_pitching_stats if row.team_id == team.id]
        for row in batting_rows:
            accumulator.doubles += row.doubles
            accumulator.at_bats += row.at_bats
            accumulator.batting_hits += row.hits
            accumulator.walks += row.walks
            accumulator.hit_by_pitch += row.hit_by_pitch
            accumulator.sacrifice_flies += row.sacrifice_flies
            accumulator.triples += row.triples
            accumulator.home_runs += row.home_runs
            accumulator.stolen_bases += row.stolen_bases
        for row in pitching_rows:
            accumulator.innings_outs += row.innings_outs
            accumulator.pitching_hits_allowed += row.hits_allowed
            accumulator.pitching_walks_allowed += row.walks_allowed
            accumulator.earned_runs += row.earned_runs
        recent_games.append(
            {
                "game_id": game.kbo_game_id,
                "game_date": game.game_date.isoformat(),
                "series_code": game.series_code,
                "stadium": game.stadium,
                "result": "W" if runs_for > runs_against else "L" if runs_for < runs_against else "D",
                "opponent_team_code": game.away_team.team_code if is_home else game.home_team.team_code,
                "team_score": runs_for,
                "opponent_score": runs_against,
            }
        )

    batting_totals = BattingTotals(
        at_bats=accumulator.at_bats,
        hits=accumulator.batting_hits,
        doubles=accumulator.doubles,
        triples=accumulator.triples,
        home_runs=accumulator.home_runs,
        strikeouts=0,
        walks=accumulator.walks,
        hit_by_pitch=accumulator.hit_by_pitch,
        sacrifice_flies=accumulator.sacrifice_flies,
    )
    singles = max(batting_totals.hits - batting_totals.doubles - batting_totals.triples - batting_totals.home_runs, 0)
    total_bases = singles + batting_totals.doubles * 2 + batting_totals.triples * 3 + batting_totals.home_runs * 4
    obp = safe_ratio(batting_totals.hits + batting_totals.walks + batting_totals.hit_by_pitch, batting_totals.at_bats + batting_totals.walks + batting_totals.hit_by_pitch + batting_totals.sacrifice_flies)
    slg = safe_ratio(total_bases, batting_totals.at_bats)
    ops = round(obp + slg, 3) if obp is not None and slg is not None else None
    era = round(accumulator.earned_runs * 27 / accumulator.innings_outs, 3) if accumulator.innings_outs > 0 else None
    league_batting = session.execute(select(LeagueSeasonBattingContext).where(LeagueSeasonBattingContext.season_id == season, LeagueSeasonBattingContext.series_code == (series_code or "regular"))).scalar_one_or_none()
    league_pitching = session.execute(select(LeagueSeasonPitchingContext).where(LeagueSeasonPitchingContext.season_id == season, LeagueSeasonPitchingContext.series_code == (series_code or "regular"))).scalar_one_or_none()
    ops_plus = round((ops / league_batting.ops) * 100, 1) if ops is not None and league_batting and league_batting.ops else None
    era_plus = round((league_pitching.era / era) * 100, 1) if era is not None and era > 0 and league_pitching and league_pitching.era else None

    return {
        "season": season,
        "series_code": series_code,
        "team_code": team.team_code,
        "team_name": team.team_name,
        "wins": accumulator.wins,
        "losses": accumulator.losses,
        "draws": accumulator.draws,
        "win_pct": safe_ratio(accumulator.wins, accumulator.wins + accumulator.losses),
        "runs_scored": accumulator.runs_scored,
        "runs_allowed": accumulator.runs_allowed,
        "run_diff": accumulator.runs_scored - accumulator.runs_allowed,
        "hits": accumulator.hits,
        "doubles": accumulator.doubles,
        "stolen_bases": accumulator.stolen_bases,
        "batting_avg": safe_ratio(accumulator.batting_hits, accumulator.at_bats),
        "ops": ops,
        "era": era,
        "whip": safe_ratio(accumulator.pitching_hits_allowed + accumulator.pitching_walks_allowed, accumulator.innings_outs / 3 if accumulator.innings_outs > 0 else 0),
        "ops_plus": ops_plus,
        "era_plus": era_plus,
        "last_ten": f"{accumulator.recent_results[-10:].count('W')}-{accumulator.recent_results[-10:].count('L')}",
        "streak": format_streak(accumulator.recent_results),
        "recent_games": recent_games[:10],
    }
