from app.services.derived_stats import BattingTotals, PitchingTotals, derive_batting_metrics, derive_pitching_metrics


def test_derive_batting_metrics() -> None:
    totals = BattingTotals(
        at_bats=10,
        hits=5,
        doubles=1,
        triples=1,
        home_runs=1,
        walks=2,
        hit_by_pitch=1,
        sacrifice_flies=1,
    )

    metrics = derive_batting_metrics(totals)

    assert metrics["singles"] == 2
    assert metrics["total_bases"] == 11
    assert metrics["avg"] == 0.5
    assert metrics["obp"] == 0.615
    assert metrics["slg"] == 1.1
    assert metrics["ops"] == 1.715


def test_derive_pitching_metrics() -> None:
    totals = PitchingTotals(innings_outs=12, hits_allowed=4, walks_allowed=2, strikeouts=6)

    metrics = derive_pitching_metrics(totals)

    assert metrics["whip"] == 1.5
    assert metrics["k_per_9"] == 13.5
    assert metrics["bb_per_9"] == 4.5
    assert metrics["kbb"] == 3.0
