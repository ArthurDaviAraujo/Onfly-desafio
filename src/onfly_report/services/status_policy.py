"""Política de status das reservas."""

from __future__ import annotations

CONFIRMED = "CONFIRMED"
CANCELLED = "CANCELLED"
NO_SHOW = "NO_SHOW"

KNOWN_STATUSES = (CONFIRMED, CANCELLED, NO_SHOW)


def is_billable(status: str) -> bool:
    """Indica se a reserva entra nos totais financeiros e de noites.

    Só CONFIRMED é faturável; CANCELLED e NO_SHOW contam apenas nas contagens por status.
    """
    return status == CONFIRMED
