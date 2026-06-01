"""
Campos de modelo con cifrado simétrico Fernet.

La clave se obtiene de `settings.ODOO_ENCRYPTION_KEY`. Si no está
definida, el campo lanza `ImproperlyConfigured` al primer uso.

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
    key = getattr(settings, 'ODOO_ENCRYPTION_KEY', '') or ''
    if not key:
        raise ImproperlyConfigured(
            'ODOO_ENCRYPTION_KEY no está configurada. '
            'Genera una con Fernet.generate_key() y añádela al .env.'
        )
    if isinstance(key, str):
        key = key.encode('utf-8')
    try:
        return Fernet(key)
    except (ValueError, TypeError) as exc:
        raise ImproperlyConfigured(
            f'ODOO_ENCRYPTION_KEY no es una clave Fernet válida: {exc}'
        ) from exc


class EncryptedTextField(models.TextField):
    """
    Campo de texto cifrado en BD con Fernet.

    En Python se manipula como string plano; el cifrado/descifrado es
    transparente. Valores `None` o cadena vacía se almacenan tal cual.
    """

    description = 'TextField cifrado con Fernet'

    def from_db_value(self, value, expression, connection):  # noqa: D401
        if value is None or value == '':
            return value
        try:
            return _get_fernet().decrypt(value.encode('utf-8')).decode('utf-8')
        except InvalidToken:
            # Valor corrupto o clave rotada — devolvemos cadena vacía
            # para no romper la app, pero el caller debería detectarlo.
            return ''

    def to_python(self, value):
        if value is None or value == '':
            return value
        # Si ya es plano (formulario) lo devolvemos; si es token Fernet,
        # intentamos descifrar (caso poco frecuente pero seguro).
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
