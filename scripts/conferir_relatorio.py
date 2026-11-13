"""Conferência independente do relatório gerado pelo CLI.

Recalcula o relatório direto dos CSVs, só com a biblioteca padrão e SEM importar `onfly_report`,
seguindo as regras do README, e compara campo a campo com o JSON gerado pelo CLI.

Uso (na raiz do projeto):
    python scripts/conferir_relatorio.py \
        --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --report output/report.json [--top 5]

Sai com 0 se tudo bater (exceto `generated_at`, cujo offset é conferido à parte) e 1 se houver divergência.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path


def money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def recompute(input_path: Path, rates_path: Path, top: int) -> dict:
    with rates_path.open(encoding="utf-8-sig", newline="") as handle:
        rates = {row["currency"].strip().upper(): Decimal(row["rate_to_brl"]) for row in csv.DictReader(handle)}
    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    statuses = Counter(row["status"].strip() for row in rows)
    months: dict[str, list] = defaultdict(lambda: [0, 0, Decimal(0)])
    hotels: dict[str, list] = defaultdict(lambda: ["", 0, Decimal(0)])
    nights_total, amount_total = 0, Decimal(0)

    for row in rows:
        if row["status"].strip() != "CONFIRMED":
            continue
        checkin = date.fromisoformat(row["checkin_date"])
        nights = (date.fromisoformat(row["checkout_date"]) - checkin).days * int(row["rooms"])
        brl = Decimal(row["amount"]) * rates[row["currency"].strip().upper()]
        nights_total += nights
        amount_total += brl
        month = months[checkin.isoformat()[:7]]
        month[0] += 1
        month[1] += nights
        month[2] += brl
        hotel = hotels[row["hotel_id"].strip()]
        hotel[0] = row["hotel_name"].strip()
        hotel[1] += nights
        hotel[2] += brl

    ranking = sorted(hotels.items(), key=lambda item: (-item[1][2], item[0]))[:top]
    return {
        "report_version": "1.0",
        "summary": {
            "total_reservations": len(rows),
            "confirmed_reservations": statuses["CONFIRMED"],
            "cancelled_reservations": statuses["CANCELLED"],
            "no_show_reservations": statuses["NO_SHOW"],
            "total_room_nights": nights_total,
            "total_amount_brl": money(amount_total),
            "average_nightly_rate_brl": money(amount_total / nights_total if nights_total else Decimal(0)),
        },
        "by_month": [
            {"month": key, "reservations": value[0], "room_nights": value[1], "total_brl": money(value[2])}
            for key, value in sorted(months.items())
        ],
        "top_hotels": [
            {"hotel_id": key, "hotel_name": value[0], "room_nights": value[1], "total_brl": money(value[2])}
            for key, value in ranking
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--rates", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    expected = recompute(args.input, args.rates, args.top)
    actual = json.loads(args.report.read_text(encoding="utf-8"))
    problems = []

    offset = datetime.fromisoformat(actual.get("generated_at", "")).utcoffset()
    if offset != timedelta(hours=-3):
        problems.append(f"generated_at fora de -03:00: {actual.get('generated_at')}")
    actual_without_time = {key: value for key, value in actual.items() if key != "generated_at"}
    if list(actual_without_time) != list(expected):
        problems.append(f"chaves de topo diferentes: {list(actual_without_time)}")
    for key in expected:
        if actual.get(key) != expected[key]:
            problems.append(f"{key} diverge:\n  esperado {expected[key]}\n  obtido   {actual.get(key)}")

    summary = expected["summary"]
    print(f"Recalculado de forma independente a partir de {args.input}:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print(f"  meses: {len(expected['by_month'])} | hotéis no ranking: {len(expected['top_hotels'])}")
    print(
        "  checagens cruzadas: status somam o total =",
        summary["confirmed_reservations"] + summary["cancelled_reservations"] + summary["no_show_reservations"]
        == summary["total_reservations"],
        "| reservas por mês somam as confirmadas =",
        sum(item["reservations"] for item in expected["by_month"]) == summary["confirmed_reservations"],
        "| noites por mês somam o total =",
        sum(item["room_nights"] for item in expected["by_month"]) == summary["total_room_nights"],
    )

    if problems:
        print("\nDIVERGÊNCIAS:")
        print("\n".join(problems))
        return 1
    print("\nOK: o relatório do CLI bate com o recálculo independente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
