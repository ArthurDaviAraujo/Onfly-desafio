"""Testes adicionais: desempate e limite do ranking de hotéis."""

from helpers import run_cli


def test_tie_is_broken_by_hotel_id_ascending(tmp_path):
    """Mesmo total, entrada em ordem inversa: o ranking volta a ficar por hotel_id."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "500.00"},
            {"reservation_id": "R-2", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "500.00"},
        ],
    )

    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]


def test_ranking_uses_exact_total_not_rounded(tmp_path):
    """Os dois serializam "100.00", mas H02 tem mais dinheiro exato e vem antes de H01."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "100.001"},
            {"reservation_id": "R-2", "hotel_id": "H02", "amount": "100.004"},
        ],
    )

    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H02", "H01"]
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == ["100.00", "100.00"]


def test_hotel_totals_aggregate_several_reservations(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "300.00"},
            {"reservation_id": "R-2", "hotel_id": "H02", "amount": "500.00"},
            {
                "reservation_id": "R-3",
                "hotel_id": "H01",
                "amount": "300.00",
                "checkin_date": "2025-01-20",
                "checkout_date": "2025-01-22",
            },
        ],
    )

    assert report["top_hotels"][0] == {
        "hotel_id": "H01",
        "hotel_name": "Hotel Teste",
        "room_nights": 3,
        "total_brl": "600.00",
    }


def test_top_returns_fewer_items_when_there_are_fewer_hotels(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01"},
            {"reservation_id": "R-2", "hotel_id": "H02"},
        ],
        top=10,
    )

    assert len(report["top_hotels"]) == 2


def test_default_top_is_five(tmp_path):
    from cli_runner import run_cli_raw

    rows = [{"reservation_id": f"R-{i}", "hotel_id": f"H{i:02d}", "amount": f"{i}00.00"} for i in range(1, 8)]
    result = run_cli_raw(tmp_path, rows)

    assert result.returncode == 0, result.stderr
    assert [hotel["hotel_id"] for hotel in result.report()["top_hotels"]] == ["H07", "H06", "H05", "H04", "H03"]
