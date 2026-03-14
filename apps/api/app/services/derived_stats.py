from dataclasses import dataclass


def safe_ratio(numerator: float, denominator: float) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 3)


@dataclass(slots=True)
class BattingTotals:
    at_bats: int
    hits: int
    doubles: int
    triples: int
    home_runs: int
    walks: int
    hit_by_pitch: int
    sacrifice_flies: int


@dataclass(slots=True)
class PitchingTotals:
    innings_outs: int
    hits_allowed: int
    walks_allowed: int
    strikeouts: int


def derive_batting_metrics(totals: BattingTotals) -> dict[str, float | int | None]:
    singles = max(totals.hits - totals.doubles - totals.triples - totals.home_runs, 0)
    total_bases = singles + (totals.doubles * 2) + (totals.triples * 3) + (totals.home_runs * 4)
    avg = safe_ratio(totals.hits, totals.at_bats)
    obp = safe_ratio(
        totals.hits + totals.walks + totals.hit_by_pitch,
        totals.at_bats + totals.walks + totals.hit_by_pitch + totals.sacrifice_flies,
    )
    slg = safe_ratio(total_bases, totals.at_bats)
    ops = round(obp + slg, 3) if obp is not None and slg is not None else None

    return {
        "singles": singles,
        "total_bases": total_bases,
        "avg": avg,
        "obp": obp,
        "slg": slg,
        "ops": ops,
    }


def derive_pitching_metrics(totals: PitchingTotals) -> dict[str, float | None]:
    innings = totals.innings_outs / 3
    whip = safe_ratio(totals.walks_allowed + totals.hits_allowed, innings)
    k_per_9 = safe_ratio(totals.strikeouts * 9, innings)
    bb_per_9 = safe_ratio(totals.walks_allowed * 9, innings)
    kbb = safe_ratio(totals.strikeouts, totals.walks_allowed)

    return {
        "whip": whip,
        "k_per_9": k_per_9,
        "bb_per_9": bb_per_9,
        "kbb": kbb,
    }
