"""Cálculo de noites ocupadas."""

from __future__ import annotations

from datetime import date


def calculate_room_nights(checkin: date, checkout: date, rooms: int) -> int:
    """Calcula noites de quarto: diferença de dias (não inclusiva) vezes quartos.

    Subtrai as datas completas, então a virada de mês e de ano é considerada.
    """
    return (checkout - checkin).days * rooms
