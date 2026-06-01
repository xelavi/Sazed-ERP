"""
Campo de modelo con cifrado simétrico Fernet para `ecommerce_sync`.

Reutiliza la misma clave que la integración Odoo para no exigir una
variable nueva: lee `settings.ECOMMERCE_ENCRYPTION_KEY` y, si no está,
cae a `settings.ODOO_ENCRYPTION_KEY`.

Generación de clave:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
from __future__ import annotations

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    key = (
        getattr(settings, 'ECOMMERCE_ENCRYPTION_KEY', '')
        or getattr(settings, 'ODOO_ENCRYPTION_KEY', '')
        or ''
    )
    if not key:
        raise ImproperlyConfigured(
            'ECOMMERCE_ENCRYPTION_KEY (o ODOO_ENCRYPTION_KEY) no está '
            'configurada. Genera una con Fernet.generate_key() y añádela al .env.'
        )
    if isinstance(key, str):
        key = key.encode('utf-8')
    try:
        return Fernet(key)
    except (ValueError, TypeError) as exc:
        raise ImproperlyConfigured(
            f'La clave de cifrado no es una clave Fernet válida: {exc}'
        ) from exc


class EncryptedTextField(models.TextField):
    """TextField cifrado en BD con Fernet; en Python se usa como texto plano."""

    description = 'TextField cifrado con Fernet'

    def from_db_value(self, value, expression, connection):  # noqa: D401
        if value is None or value == '':
            return value
        try:
            return _get_fernet().decrypt(value.encode('utf-8')).decode('utf-8')
        except InvalidToken:
            return ''

    def to_python(self, value):
        if value is None or value == '':
            return value
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        try:
            return _get_fernet().decrypt(value.encode('utf-8')).decode('utf-8')
        except InvalidToken:
            return value

    def get_prep_value(self, value):
        if value is None or value == '':
            return value
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        return _get_fernet().encrypt(value.encode('utf-8')).decode('utf-8')
