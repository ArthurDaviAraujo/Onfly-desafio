"""Testes adicionais de unidade: regras isoladas, sem subprocesso."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from helpers import BASE

from onfly_report.exceptions import InputFileError
from onfly_report.models import RawRow
from onfly_report.services.currency_converter import convert_to_brl
from onfly_report.services.report_builder import ReportBuilder, format_money
from onfly_report.services.status_policy import is_billable
from onfly_report.services.stay_calculator import calculate_room_nights

RATES = {"BRL": Decimal("1"), "USD": Decimal("5.42"), "EUR": Decimal("5.88")}


@pytest.mark.parametrize(
    ("checkin", "checkout", "rooms", "expected"),
    [
        (date(2025, 1, 10), date(2025, 1, 13), 1, 3),
        (date(2025, 1, 30), date(2025, 2, 2), 1, 3),
        (date(2024, 12, 30), date(2025, 1, 2), 2, 6),
        (date(2024, 2, 28), date(2024, 3, 1), 3, 6),  # ano bissexto: 28/02 -> 01/03 = 2 noites
    ],
)
def test_calculate_room_nights(checkin, checkout, rooms, expected):
    assert calculate_room_nights(checkin, checkout, rooms) == expected


@pytest.mark.parametrize(("status", "billable"), [("CONFIRMED", True), ("CANCELLED", False), ("NO_SHOW", False)])
def test_only_confirmed_is_billable(status, billable):
    assert is_billable(status) is billable


def test_convert_to_brl_multiplies_and_stays_decimal():
    result = convert_to_brl(Decimal("33.33"), "USD", RATES)

    assert isinstance(result, Decimal)
    assert result == Decimal("180.6486")


@pytest.mark.parametrize(
    ("amount", "rate", "expected"),
    [
        ("1.1", "1.1", "1.21"),  # em float: 1.2100000000000002
        ("1234567.891234567891", "1", "1234567.891234567891"),  # float perde os últimos dígitos
    ],
)
def test_convert_to_brl_is_exact_without_float(amount, rate, expected):
    assert convert_to_brl(Decimal(amount), "XXX", {"XXX": Decimal(rate)}) == Decimal(expected)


def test_convert_to_brl_without_rate_is_input_error():
    with pytest.raises(InputFileError):
        convert_to_brl(Decimal("1"), "GBP", RATES)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("0", "0.00"), ("0.005", "0.01"), ("2.675", "2.68"), ("1234.5", "1234.50"), ("396170", "396170.00")],
)
def test_format_money_half_up_two_places(value, expected):
    assert format_money(Decimal(value)) == expected


class _StubReservations:
    def read(self):
        return [RawRow(line_number=2, values=dict(BASE))]


class _StubRates:
    def read(self):
        return dict(RATES)


@pytest.mark.parametrize(
    "now",
    [
        datetime(2025, 7, 1, 13, 0, tzinfo=timezone.utc),
        datetime(2025, 7, 1, 10, 0),
        datetime(2025, 7, 1, 10, 0, tzinfo=timezone(timedelta(hours=-3))),
    ],
)
def test_injected_now_is_serialized_with_fixed_offset(now):
    report = ReportBuilder(_StubReservations(), _StubRates(), now=now).build()

    assert report["generated_at"] == "2025-07-01T10:00:00-03:00"
