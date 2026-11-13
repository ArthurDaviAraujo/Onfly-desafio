"""Testes adicionais: leitura completa do arquivo de reservas."""

import csv

from cli_runner import run_cli_raw, write_reservations
from helpers import PROJECT_ROOT, run_cli


def test_reads_beyond_200_rows_and_last_row_counts(tmp_path):
    """O leitor parava em 200 linhas; a 201ª reserva precisa entrar nos totais e no ranking."""
    rows = [{"reservation_id": f"R-{i}", "amount": "10.00"} for i in range(1, 201)]
    rows.append({"reservation_id": "R-201", "hotel_id": "H99", "hotel_name": "Hotel Final", "amount": "5000.00"})

    report = run_cli(tmp_path, rows, top=1)

    assert report["summary"]["total_reservations"] == 201
    assert report["summary"]["confirmed_reservations"] == 201
    assert report["summary"]["total_room_nights"] == 201
    assert report["summary"]["total_amount_brl"] == "7000.00"
    assert report["top_hotels"][0]["hotel_id"] == "H99"


def test_accepts_csv_with_utf8_bom(tmp_path):
    """Exportações de planilha costumam gravar BOM; o cabeçalho deve ser reconhecido mesmo assim."""
    input_path = write_reservations(tmp_path / "bom.csv", [{"reservation_id": "R-1"}], bom=True)

    result = run_cli_raw(tmp_path, input_path=input_path)

    assert result.returncode == 0, result.stderr
    assert result.report()["summary"]["total_reservations"] == 1


def test_full_dataset_counts_every_reservation(tmp_path):
    """No CSV principal, total = linhas do arquivo e a soma das contagens por status fecha com o total."""
    input_path = PROJECT_ROOT / "data" / "reservas_hoteis.csv"
    with input_path.open(encoding="utf-8", newline="") as handle:
        expected_rows = sum(1 for _ in csv.DictReader(handle))

    result = run_cli_raw(
        tmp_path,
        input_path=input_path,
        rates_text=(PROJECT_ROOT / "data" / "taxas_cambio.csv").read_text(encoding="utf-8"),
    )
    assert result.returncode == 0, result.stderr
    summary = result.report()["summary"]

    assert expected_rows == 300
    assert summary["total_reservations"] == expected_rows
    assert (
        summary["confirmed_reservations"] + summary["cancelled_reservations"] + summary["no_show_reservations"]
        == expected_rows
    )
