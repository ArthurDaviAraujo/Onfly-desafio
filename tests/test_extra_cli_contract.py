"""Testes adicionais: contrato do CLI (schema, tipos, stdout e códigos de saída)."""

import re
from datetime import datetime, timedelta

import pytest
from cli_runner import run_cli_raw, write_reservations
from helpers import COLUMNS

MONEY = re.compile(r"^\d+\.\d{2}$")


def test_report_schema_and_types(tmp_path):
    result = run_cli_raw(tmp_path, [{"reservation_id": "R-1", "amount": "1234.5"}])
    assert result.returncode == 0, result.stderr
    report = result.report()

    assert list(report) == ["report_version", "generated_at", "summary", "by_month", "top_hotels"]
    assert report["report_version"] == "1.0"
    assert list(report["summary"]) == [
        "total_reservations",
        "confirmed_reservations",
        "cancelled_reservations",
        "no_show_reservations",
        "total_room_nights",
        "total_amount_brl",
        "average_nightly_rate_brl",
    ]
    assert list(report["by_month"][0]) == ["month", "reservations", "room_nights", "total_brl"]
    assert list(report["top_hotels"][0]) == ["hotel_id", "hotel_name", "room_nights", "total_brl"]

    summary = report["summary"]
    for key in ("total_reservations", "confirmed_reservations", "total_room_nights"):
        assert type(summary[key]) is int
    for money in (summary["total_amount_brl"], summary["average_nightly_rate_brl"], report["by_month"][0]["total_brl"]):
        assert isinstance(money, str) and MONEY.match(money)
    assert summary["total_amount_brl"] == "1234.50"


def test_generated_at_uses_fixed_minus_three_offset(tmp_path):
    result = run_cli_raw(tmp_path, [{"reservation_id": "R-1"}])
    assert result.returncode == 0, result.stderr

    generated_at = datetime.fromisoformat(result.report()["generated_at"])
    assert generated_at.utcoffset() == timedelta(hours=-3)
    assert result.report()["generated_at"].endswith("-03:00")


def test_stdout_prints_summary_and_logs_stay_on_stderr(tmp_path):
    result = run_cli_raw(tmp_path, [{"reservation_id": "R-1", "amount": "100.00"}])

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "Reservas: 1 | Confirmadas: 1 | Noites: 1 | Total BRL: 100.00"


def test_default_output_path_is_created(tmp_path):
    """Sem --output, grava em output/report.json relativo ao diretório atual, criando a pasta."""
    result = run_cli_raw(tmp_path, [{"reservation_id": "R-1"}], with_output=False, cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "output" / "report.json").is_file()


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ({"status": "PENDING"}, "status desconhecido"),
        ({"checkin_date": "2025-01-10", "checkout_date": "2025-01-10"}, "check-out"),
        ({"rooms": "0"}, "quartos"),
        ({"amount": "abc"}, "inválida"),
        ({"amount": "NaN"}, "valor inválido"),
        ({"checkin_date": "10/01/2025"}, "inválida"),
        ({"currency": "GBP"}, "moeda sem taxa"),
    ],
)
def test_invalid_reservation_exits_with_code_2(tmp_path, row, message):
    result = run_cli_raw(tmp_path, [{"reservation_id": "R-1", **row}])

    assert result.returncode == 2
    assert message in result.stderr
    assert not result.output_path.exists()


def test_missing_input_file_exits_with_code_2(tmp_path):
    result = run_cli_raw(tmp_path, input_path=tmp_path / "nao-existe.csv")

    assert result.returncode == 2


def test_missing_required_column_exits_with_code_2(tmp_path):
    columns = [column for column in COLUMNS if column != "amount"]
    input_path = write_reservations(tmp_path / "sem-amount.csv", [{"reservation_id": "R-1"}], columns=columns)

    result = run_cli_raw(tmp_path, input_path=input_path)

    assert result.returncode == 2
    assert "amount" in result.stderr


@pytest.mark.parametrize("rate", ["0", "-1", "abc", "NaN", "Infinity"])
def test_invalid_rate_exits_with_code_2(tmp_path, rate):
    result = run_cli_raw(
        tmp_path,
        [{"reservation_id": "R-1"}],
        rates_text=f"currency,rate_to_brl\nBRL,{rate}\n",
    )

    assert result.returncode == 2


@pytest.mark.parametrize("top", ["0", "-1", "abc"])
def test_invalid_top_exits_with_code_2(tmp_path, top):
    result = run_cli_raw(tmp_path, [{"reservation_id": "R-1"}], extra_args=["--top", top])

    assert result.returncode == 2


def test_missing_required_argument_exits_with_code_2(tmp_path):
    import os
    import subprocess
    import sys

    from helpers import PROJECT_ROOT, SRC_DIR

    environment = {**os.environ, "PYTHONPATH": str(SRC_DIR)}
    process = subprocess.run(
        [sys.executable, "-m", "onfly_report", "--input", "x.csv"],
        cwd=str(PROJECT_ROOT),
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert process.returncode == 2
    assert "--rates" in process.stderr
