"""Testes adicionais: câmbio, exatidão em Decimal e arredondamento half-up só na serialização."""

from helpers import run_cli


def test_eur_conversion_multiplies_by_rate(tmp_path):
    report = run_cli(tmp_path, [{"reservation_id": "R-1", "currency": "EUR", "amount": "100.00"}])

    assert report["summary"]["total_amount_brl"] == "588.00"


def test_sums_exact_values_and_rounds_only_once(tmp_path):
    """3 x 0.005 = 0.015 -> "0.02". Arredondar cada item antes de somar daria "0.03"."""
    report = run_cli(
        tmp_path,
        [{"reservation_id": f"R-{i}", "amount": "0.005"} for i in range(1, 4)],
    )

    assert report["summary"]["total_amount_brl"] == "0.02"


def test_rounding_is_half_up(tmp_path):
    """0.125 vira "0.13" com half-up (half-even daria "0.12")."""
    report = run_cli(tmp_path, [{"reservation_id": "R-1", "amount": "0.125"}])

    assert report["summary"]["total_amount_brl"] == "0.13"


def test_converted_cents_are_not_lost_through_float(tmp_path):
    """USD 33.33 x 5.42 = 180.6486 -> "180.65"; a soma exata de vários itens não acumula erro."""
    report = run_cli(
        tmp_path,
        [{"reservation_id": f"R-{i}", "currency": "USD", "amount": "33.33"} for i in range(1, 11)],
    )

    assert report["summary"]["total_amount_brl"] == "1806.49"


def test_average_uses_exact_totals(tmp_path):
    """200 / 3 noites = 66.666... -> "66.67", calculado sobre os totais exatos."""
    report = run_cli(
        tmp_path,
        [{"reservation_id": "R-1", "amount": "200.00", "checkin_date": "2025-01-10", "checkout_date": "2025-01-13"}],
    )

    assert report["summary"]["average_nightly_rate_brl"] == "66.67"
