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
    strikeouts: int
    walks: int
    hit_by_pitch: int
    sacrifice_flies: int
    intentional_walks: int = 0


@dataclass(slots=True)
class PitchingTotals:
    innings_outs: int
    hits_allowed: int
    walks_allowed: int
    strikeouts: int
    hit_by_pitch_allowed: int = 0
    home_runs_allowed: int = 0


def derive_batting_metrics(totals: BattingTotals) -> dict[str, float | int | None]:
    singles = max(totals.hits - totals.doubles - totals.triples - totals.home_runs, 0)
    total_bases = singles + (totals.doubles * 2) + (totals.triples * 3) + (totals.home_runs * 4)
    plate_appearances = totals.at_bats + totals.walks + totals.hit_by_pitch + totals.sacrifice_flies
    avg = safe_ratio(totals.hits, totals.at_bats)
    obp = safe_ratio(
        totals.hits + totals.walks + totals.hit_by_pitch,
        totals.at_bats + totals.walks + totals.hit_by_pitch + totals.sacrifice_flies,
    )
    slg = safe_ratio(total_bases, totals.at_bats)
    ops = round(obp + slg, 3) if obp is not None and slg is not None else None
    iso = round(slg - avg, 3) if slg is not None and avg is not None else None
    babip = safe_ratio(
        totals.hits - totals.home_runs,
        totals.at_bats - totals.strikeouts - totals.home_runs + totals.sacrifice_flies,
    )
    bb_rate = safe_ratio(totals.walks, plate_appearances)
    k_rate = safe_ratio(totals.strikeouts, plate_appearances)

    return {
        "plate_appearances": plate_appearances,
        "singles": singles,
        "total_bases": total_bases,
        "avg": avg,
        "obp": obp,
        "slg": slg,
        "ops": ops,
        "iso": iso,
        "babip": babip,
        "bb_rate": bb_rate,
        "k_rate": k_rate,
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


def derive_woba_metrics(
    totals: BattingTotals,
    *,
    unintentional_walk_weight: float,
    hit_by_pitch_weight: float,
    single_weight: float,
    double_weight: float,
    triple_weight: float,
    home_run_weight: float,
    woba_scale: float,
    league_woba: float,
    league_runs_per_pa: float,
) -> dict[str, float | None]:
    singles = max(totals.hits - totals.doubles - totals.triples - totals.home_runs, 0)
    unintentional_walks = max(totals.walks - totals.intentional_walks, 0)
    denominator = totals.at_bats + unintentional_walks + totals.hit_by_pitch + totals.sacrifice_flies
    numerator = (
        unintentional_walk_weight * unintentional_walks
        + hit_by_pitch_weight * totals.hit_by_pitch
        + single_weight * singles
        + double_weight * totals.doubles
        + triple_weight * totals.triples
        + home_run_weight * totals.home_runs
    )
    woba = safe_ratio(numerator, denominator)
    plate_appearances = totals.at_bats + totals.walks + totals.hit_by_pitch + totals.sacrifice_flies
    if woba is None or plate_appearances == 0:
        return {"woba": None, "wrc": None, "wrc_plus": None}

    wraa = ((woba - league_woba) / woba_scale) * plate_appearances
    wrc = wraa + (league_runs_per_pa * plate_appearances)
    wrc_plus = (((wraa / plate_appearances) + league_runs_per_pa) / league_runs_per_pa) * 100 if league_runs_per_pa > 0 else None
    return {
        "woba": round(woba, 3),
        "wrc": round(wrc, 1),
        "wrc_plus": round(wrc_plus, 1) if wrc_plus is not None else None,
    }


def derive_fip_metric(totals: PitchingTotals, *, fip_constant: float) -> float | None:
    innings = totals.innings_outs / 3
    if innings == 0:
        return None
    raw_fip = ((13 * totals.home_runs_allowed) + (3 * (totals.walks_allowed + totals.hit_by_pitch_allowed)) - (2 * totals.strikeouts)) / innings
    return round(raw_fip + fip_constant, 3)
