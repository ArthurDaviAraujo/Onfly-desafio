"""Utilitários dos testes adicionais.

Complementa `helpers.py` (fornecido, não alterado) com execução do CLI que devolve o processo
inteiro, para testar códigos de saída, stdout e entradas inválidas.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from helpers import BASE, COLUMNS, PROJECT_ROOT, SRC_DIR

DEFAULT_RATES = "currency,rate_to_brl\nBRL,1.000000\nUSD,5.420000\nEUR,5.880000\n"


@dataclass
class CliResult:
    returncode: int
    stdout: str
    stderr: str
    output_path: Path

    def report(self) -> dict:
        return json.loads(self.output_path.read_text(encoding="utf-8"))


def write_reservations(path: Path, rows: list[dict[str, str]], columns: list[str] = COLUMNS, bom: bool = False) -> Path:
    """Grava um CSV de reservas preenchendo as colunas omitidas com a linha base."""
    encoding = "utf-8-sig" if bom else "utf-8"
    with path.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows({**BASE, **row} for row in rows)
    return path


def run_cli_raw(
    tmp_path: Path,
    rows: list[dict[str, str]] | None = None,
    *,
    extra_args: list[str] | None = None,
    input_path: Path | None = None,
    rates_text: str = DEFAULT_RATES,
    with_output: bool = True,
    cwd: Path = PROJECT_ROOT,
) -> CliResult:
    """Executa o CLI e devolve código de saída, stdout, stderr e caminho do relatório."""
    if input_path is None:
        input_path = write_reservations(tmp_path / "reservas.csv", rows or [])
    rates_path = tmp_path / "rates.csv"
    rates_path.write_text(rates_text, encoding="utf-8")
    output_path = tmp_path / "report.json"

    args = [sys.executable, "-m", "onfly_report", "--input", str(input_path), "--rates", str(rates_path)]
    if with_output:
        args += ["--output", str(output_path)]
    args += extra_args or []

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    # Fixa UTF-8 nos dois lados para as mensagens com acento independerem da codificação do sistema.
    environment["PYTHONIOENCODING"] = "utf-8"
    process = subprocess.run(
        args, cwd=str(cwd), env=environment, capture_output=True, text=True, encoding="utf-8", timeout=60
    )
    return CliResult(process.returncode, process.stdout, process.stderr, output_path)
