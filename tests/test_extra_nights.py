"""Testes adicionais: noites na virada de ano, com vários quartos, e mês pelo check-in."""

from helpers import run_cli


def test_nights_across_year_boundary_with_two_rooms(tmp_path):
    """30/12 a 02/01 são 3 noites; com 2 quartos, 6 noites de quarto, agrupadas no mês do check-in."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "checkin_date": "2024-12-30",
                "checkout_date": "2025-01-02",
                "rooms": "2",
                "amount": "600.00",
            }
        ],
    )

    assert report["summary"]["total_room_nights"] == 6
    assert report["summary"]["average_nightly_rate_brl"] == "100.00"
    assert report["by_month"] == [{"month": "2024-12", "reservations": 1, "room_nights": 6, "total_brl": "600.00"}]


def test_by_month_is_sorted_chronologically(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "checkin_date": "2025-03-01", "checkout_date": "2025-03-02"},
            {"reservation_id": "R-2", "checkin_date": "2024-11-01", "checkout_date": "2024-11-02"},
            {"reservation_id": "R-3", "checkin_date": "2025-01-01", "checkout_date": "2025-01-02"},
        ],
    )

    assert [month["month"] for month in report["by_month"]] == ["2024-11", "2025-01", "2025-03"]
