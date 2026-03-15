from app.ingest.parsers.common import parse_innings_to_outs


def test_parse_innings_to_outs_supports_baseball_decimal_notation() -> None:
    assert parse_innings_to_outs("5.0") == 15
    assert parse_innings_to_outs("5.1") == 16
    assert parse_innings_to_outs("5.2") == 17
    assert parse_innings_to_outs("0.1") == 1
    assert parse_innings_to_outs("0.2") == 2


def test_parse_innings_to_outs_supports_fractional_text_notation() -> None:
    assert parse_innings_to_outs("3 1/3") == 10
    assert parse_innings_to_outs("2/3") == 2
    assert parse_innings_to_outs("1/3") == 1
