"""Utilidades compartidas para facturación recurrente (ventas y compras)."""
import calendar
from datetime import date

from django.db import models


class RecurrenceFrequency(models.TextChoices):
    WEEKLY = 'weekly', 'Semanal'
    MONTHLY = 'monthly', 'Mensual'
    QUARTERLY = 'quarterly', 'Trimestral'
    SEMIANNUAL = 'semiannual', 'Semestral'
    YEARLY = 'yearly', 'Anual'


_MONTHS_PER_PERIOD = {
    'monthly': 1,
    'quarterly': 3,
    'semiannual': 6,
    'yearly': 12,
}


def _add_months(d: date, months: int) -> date:
    """Suma meses a una fecha respetando el último día del mes destino."""
    total = d.month - 1 + months
    year = d.year + total // 12
    month = total % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, last_day))


def add_period(d: date, frequency: str, interval: int = 1) -> date:
    """Avanza una fecha según la frecuencia de recurrencia.

    El intervalo multiplica la frecuencia (p. ej. mensual con intervalo 2 = cada 2 meses).
    """
    interval = max(1, interval or 1)
    if frequency == RecurrenceFrequency.WEEKLY:
        from datetime import timedelta
        return d + timedelta(weeks=interval)
    months = _MONTHS_PER_PERIOD.get(frequency)
    if months is None:
        raise ValueError(f'Frecuencia de recurrencia no soportada: {frequency}')
    return _add_months(d, months * interval)
