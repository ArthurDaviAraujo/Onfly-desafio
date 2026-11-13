"""Testes adicionais: CANCELLED e NO_SHOW fora de noites, valores, by_month e top_hotels."""

from helpers import run_cli


def test_non_confirmed_stay_out_of_months_and_ranking(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "100.00", "checkin_date": "2025-01-10"},
            {
                "reservation_id": "R-2",
                "hotel_id": "H02",
                "status": "NO_SHOW",
                "amount": "9000.00",
                "checkin_date": "2025-02-10",
                "checkout_date": "2025-02-12",
            },
            {
                "reservation_id": "R-3",
                "hotel_id": "H03",
                "status": "CANCELLED",
                "amount": "8000.00",
                "checkin_date": "2025-03-10",
                "checkout_date": "2025-03-12",
            },
        ],
    )

    assert [month["month"] for month in report["by_month"]] == ["2025-01"]
    assert report["by_month"][0]["reservations"] == 1
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01"]
    assert report["summary"]["no_show_reservations"] == 1
    assert report["summary"]["cancelled_reservations"] == 1


def test_no_confirmed_reservation_yields_zeroes(tmp_path):
    """Sem noites faturáveis, a média é "0.00" e as listas ficam vazias."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "status": "CANCELLED"},
            {"reservation_id": "R-2", "status": "NO_SHOW"},
        ],
    )

    assert report["summary"] == {
        "total_reservations": 2,
        "confirmed_reservations": 0,
        "cancelled_reservations": 1,
        "no_show_reservations": 1,
        "total_room_nights": 0,
        "total_amount_brl": "0.00",
        "average_nightly_rate_brl": "0.00",
    }
    assert report["by_month"] == []
    assert report["top_hotels"] == []
