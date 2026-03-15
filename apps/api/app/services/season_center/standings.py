from app.services.derived_stats import BattingTotals, safe_ratio
from app.services.season_center.types import TeamAccumulator, TeamStandingSnapshot


def build_team_standings(accumulators: dict[str, TeamAccumulator]) -> list[TeamStandingSnapshot]:
    snapshots: list[TeamStandingSnapshot] = []

    for accumulator in accumulators.values():
        batting_totals = BattingTotals(
            at_bats=accumulator.at_bats,
            hits=accumulator.batting_hits,
            doubles=accumulator.doubles,
            triples=accumulator.triples,
            home_runs=accumulator.home_runs,
            walks=accumulator.walks,
            hit_by_pitch=accumulator.hit_by_pitch,
            sacrifice_flies=accumulator.sacrifice_flies,
        )
        singles = max(batting_totals.hits - batting_totals.doubles - batting_totals.triples - batting_totals.home_runs, 0)
        total_bases = singles + batting_totals.doubles * 2 + batting_totals.triples * 3 + batting_totals.home_runs * 4
        win_pct = safe_ratio(accumulator.wins, accumulator.wins + accumulator.losses)
        obp = safe_ratio(
            batting_totals.hits + batting_totals.walks + batting_totals.hit_by_pitch,
            batting_totals.at_bats + batting_totals.walks + batting_totals.hit_by_pitch + batting_totals.sacrifice_flies,
        )
        slg = safe_ratio(total_bases, batting_totals.at_bats)
        ops = round(obp + slg, 3) if obp is not None and slg is not None else None
        innings = accumulator.innings_outs / 3
        era = safe_ratio(accumulator.earned_runs * 9, innings)
        whip = safe_ratio(accumulator.pitching_hits_allowed + accumulator.pitching_walks_allowed, innings)
        last_ten_slice = accumulator.recent_results[-10:]
        last_ten = f"{last_ten_slice.count('W')}-{last_ten_slice.count('L')}"
        streak = format_streak(accumulator.recent_results)

        snapshots.append(
            TeamStandingSnapshot(
                rank=0,
                games=accumulator.games,
                team_code=accumulator.team_code,
                team_name=accumulator.team_name,
                wins=accumulator.wins,
                losses=accumulator.losses,
                draws=accumulator.draws,
                win_pct=win_pct,
                games_back=0.0,
                runs_scored=accumulator.runs_scored,
                runs_allowed=accumulator.runs_allowed,
                run_diff=accumulator.runs_scored - accumulator.runs_allowed,
                hits=accumulator.hits,
                doubles=accumulator.doubles,
                batting_avg=safe_ratio(batting_totals.hits, batting_totals.at_bats),
                obp=obp,
                slg=slg,
                ops=ops,
                home_runs=accumulator.home_runs,
                stolen_bases=accumulator.stolen_bases,
                era=era,
                whip=whip,
                last_ten=last_ten,
                streak=streak,
            )
        )

    snapshots.sort(
        key=lambda item: (
            -(item.win_pct if item.win_pct is not None else -1.0),
            -item.wins,
            -item.run_diff,
            -item.runs_scored,
        )
    )
    leader_wins = snapshots[0].wins
    leader_losses = snapshots[0].losses

    for index, snapshot in enumerate(snapshots, start=1):
        snapshot.rank = index
        snapshot.games_back = 0.0 if index == 1 else round(((leader_wins - snapshot.wins) + (snapshot.losses - leader_losses)) / 2, 1)

    return snapshots


def format_streak(results: list[str]) -> str:
    if not results:
        return "-"
    last = results[-1]
    if last == "D":
        return "D1"
    count = 0
    for result in reversed(results):
        if result != last:
            break
        count += 1
    return f"{last}{count}"
