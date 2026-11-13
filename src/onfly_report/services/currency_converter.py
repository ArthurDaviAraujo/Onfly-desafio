"""Conversão de valores para BRL."""

from __future__ import annotations

from decimal import Decimal


def convert_to_brl(amount: Decimal, currency: str, rates: dict[str, Decimal]) -> Decimal:
    """Converte um valor na moeda informada para BRL usando a taxa da tabela.

    A taxa é expressa em reais por unidade da moeda, então o valor é multiplicado por ela.
    A conta fica em Decimal, sem arredondar; o arredondamento só ocorre na serialização.
    """
    rate = rates[currency]
    return amount * rate
